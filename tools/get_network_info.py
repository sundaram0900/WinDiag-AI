import socket
import psutil
import subprocess
import re
import shutil
import json
import os

from langchain_core.tools import tool


# ============================================================
# FIND OOKLA SPEEDTEST EXECUTABLE
# ============================================================

def find_speedtest_executable():
    """
    Find the official Ookla Speedtest CLI executable.

    First checks PATH.
    If it is not available there, checks the standard
    WinGet installation directory.
    """

    # --------------------------------------------------------
    # 1. Check PATH
    # --------------------------------------------------------

    speedtest_path = shutil.which("speedtest")

    if speedtest_path:
        return speedtest_path


    # --------------------------------------------------------
    # 2. Check WinGet installation directory
    # --------------------------------------------------------

    winget_packages = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"
    )

    if os.path.exists(winget_packages):

        for folder in os.listdir(winget_packages):

            if folder.startswith("Ookla.Speedtest.CLI_"):

                folder_path = os.path.join(
                    winget_packages,
                    folder
                )

                executable_path = os.path.join(
                    folder_path,
                    "speedtest.exe"
                )

                if os.path.exists(executable_path):
                    return executable_path


    return None


# ============================================================
# NETWORK INFORMATION TOOL
# ============================================================

@tool
def get_network_info() -> dict:
    """
    Get basic network interface information, Wi-Fi link speed,
    local gateway latency, and packet loss.

    Link speed is the adapter's reported connection speed.
    It is NOT the actual Internet download or upload speed.
    """

    # --------------------------------------------------------
    # 1. NETWORK INTERFACES
    # --------------------------------------------------------

    interfaces = {}

    for interface_name, addresses in psutil.net_if_addrs().items():

        interface_info = []

        for address in addresses:

            if address.family in (
                socket.AF_INET,
                socket.AF_INET6
            ):

                interface_info.append({
                    "address": address.address,
                    "netmask": address.netmask
                })

        if interface_info:
            interfaces[interface_name] = interface_info


    # --------------------------------------------------------
    # 2. INTERFACE STATUS + LINK SPEED
    # --------------------------------------------------------

    interface_status = {}

    for interface_name, stats in psutil.net_if_stats().items():

        interface_status[interface_name] = {

            "is_up": stats.isup,

            # IMPORTANT:
            # This is Wi-Fi LINK SPEED.
            # It is NOT Internet speed.
            "link_speed_mbps": stats.speed,

            "duplex": str(stats.duplex)
        }


    # --------------------------------------------------------
    # 3. FIND DEFAULT GATEWAY
    # --------------------------------------------------------

    gateway = None

    try:

        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        lines = result.stdout.splitlines()

        for line in lines:

            if "Default Gateway" in line:

                gateway = line.split(":")[-1].strip()

                if gateway:
                    break

    except Exception:

        gateway = None


    # --------------------------------------------------------
    # 4. PING GATEWAY
    # --------------------------------------------------------

    latency_ms = None
    packet_loss_percent = None

    if gateway:

        try:

            result = subprocess.run(
                [
                    "ping",
                    "-n",
                    "4",
                    gateway
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            output = result.stdout


            # ------------------------------------------------
            # Packet loss
            # ------------------------------------------------

            loss_match = re.search(
                r"\((\d+)%\s*loss\)",
                output
            )

            if loss_match:

                packet_loss_percent = int(
                    loss_match.group(1)
                )


            # ------------------------------------------------
            # Average latency
            # ------------------------------------------------

            latency_match = re.search(
                r"Average\s*=\s*(\d+)ms",
                output,
                re.IGNORECASE
            )

            if latency_match:

                latency_ms = int(
                    latency_match.group(1)
                )

        except Exception:

            pass


    # --------------------------------------------------------
    # 5. RETURN NETWORK INFORMATION
    # --------------------------------------------------------

    return {

        "hostname": socket.gethostname(),

        "interfaces": interfaces,

        "interface_status": interface_status,

        "local_network_test": {

            "gateway": gateway,

            "latency_ms": latency_ms,

            "packet_loss_percent": packet_loss_percent
        }
    }


# ============================================================
# INTERNET SPEED TEST TOOL
# ============================================================

@tool
def test_internet_speed() -> dict:
    """
    Measure current Internet download and upload throughput
    using the official Ookla Speedtest CLI.

    Also returns Internet latency, jitter, ISP, and test server.

    Download and upload are actual Internet throughput
    measurements at the time of the test.

    These measurements are separate from Wi-Fi adapter
    link speed.
    """

    # --------------------------------------------------------
    # 1. FIND SPEEDTEST EXECUTABLE
    # --------------------------------------------------------

    speedtest_path = find_speedtest_executable()

    if speedtest_path is None:

        return {
            "error": (
                "Official Ookla Speedtest CLI was not found."
            )
        }


    # --------------------------------------------------------
    # 2. RUN OOKLA SPEEDTEST
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            [
                speedtest_path,

                "--accept-license",

                "--accept-gdpr",

                "--format=json",

                "--progress=no"
            ],

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="ignore",

            timeout=120
        )


        # ----------------------------------------------------
        # Check whether Ookla returned an error
        # ----------------------------------------------------

        if result.returncode != 0:

            return {

                "error": result.stderr.strip(),

                "executable": speedtest_path
            }


        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        data = json.loads(
            result.stdout
        )


        # ----------------------------------------------------
        # Convert bandwidth
        #
        # Ookla:
        # bytes / second
        #
        # We want:
        # megabits / second
        # ----------------------------------------------------

        download_mbps = (
            data["download"]["bandwidth"]
            * 8
            / 1_000_000
        )

        upload_mbps = (
            data["upload"]["bandwidth"]
            * 8
            / 1_000_000
        )


        # ----------------------------------------------------
        # Extract ping information
        # ----------------------------------------------------

        latency_ms = data["ping"]["latency"]

        jitter_ms = data["ping"]["jitter"]


        # ----------------------------------------------------
        # Extract server information
        # ----------------------------------------------------

        server_data = data.get(
            "server",
            {}
        )


        # ----------------------------------------------------
        # Return structured evidence
        # ----------------------------------------------------

        return {

            "download_mbps": round(
                download_mbps,
                2
            ),

            "upload_mbps": round(
                upload_mbps,
                2
            ),

            "latency_ms": round(
                latency_ms,
                2
            ),

            "jitter_ms": round(
                jitter_ms,
                2
            ),

            "packet_loss_percent": data.get(
                "packetLoss"
            ),

            "isp": data.get(
                "isp"
            ),

            "server": {

                "name": server_data.get(
                    "name"
                ),

                "location": server_data.get(
                    "location"
                ),

                "country": server_data.get(
                    "country"
                ),

                "id": server_data.get(
                    "id"
                )
            },

            "result_url": data.get(
                "result",
                {}
            ).get(
                "url"
            ),

            "executable": speedtest_path
        }


    # --------------------------------------------------------
    # Handle timeout
    # --------------------------------------------------------

    except subprocess.TimeoutExpired:

        return {
            "error": (
                "Internet speed test timed out."
            )
        }


    # --------------------------------------------------------
    # Handle invalid JSON
    # --------------------------------------------------------

    except json.JSONDecodeError:

        return {
            "error": (
                "Could not parse Ookla Speedtest JSON output."
            )
        }


    # --------------------------------------------------------
    # Handle any other error
    # --------------------------------------------------------

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# TEST TOOLS
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NETWORK INFORMATION")
    print("=" * 60)

    print(
        "\nTool name:",
        get_network_info.name
    )

    print(
        "\nTool description:",
        get_network_info.description
    )

    print(
        "\nTool arguments:",
        get_network_info.args
    )

    print(
        "\nTool result:"
    )

    network_result = get_network_info.invoke({})

    print(network_result)


    print("\n\n")
    print("=" * 60)
    print("INTERNET SPEED TEST")
    print("=" * 60)

    speedtest_path = find_speedtest_executable()

    print(
        "\nSpeedtest executable:",
        speedtest_path
    )

    print(
        "\nSpeedtest result:"
    )

    speed_result = test_internet_speed.invoke({})

    print(speed_result)