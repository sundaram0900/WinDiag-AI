import socket
import psutil
import subprocess
import re

from langchain_core.tools import tool


# ============================================================
# NETWORK INFORMATION TOOL
# ============================================================

@tool
def get_network_info() -> dict:
    """
    Get network interface information, Wi-Fi link speed,
    local network latency, and packet loss from the
    Windows computer.

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

            # This is LINK SPEED, NOT Internet speed.
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


            # -----------------------------------------------
            # Packet loss
            # Example:
            # "Lost = 0 (0% loss)"
            # -----------------------------------------------

            loss_match = re.search(
                r"\((\d+)%\s*loss\)",
                output
            )

            if loss_match:
                packet_loss_percent = int(
                    loss_match.group(1)
                )


            # -----------------------------------------------
            # Average latency
            # Example:
            # "Average = 4ms"
            # -----------------------------------------------

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
    # 5. RETURN STRUCTURED EVIDENCE
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
# TEST THE TOOL
# ============================================================

if __name__ == "__main__":

    print("Tool name:", get_network_info.name)

    print("Tool description:", get_network_info.description)

    print("Tool arguments:", get_network_info.args)

    print("Tool type:", type(get_network_info))

    print("\nTool result:")

    result = get_network_info.invoke({})

    print(result)