import streamlit as st

from agent.diagnostic_agent import run_diagnostic

from tools.cpu import get_cpu_usage
from tools.memory import get_memory_usage
from tools.disk import get_system_drive_storage
from tools.system import get_system_info
from dashboard_utils import get_system_snapshot
from tools.get_network_info import test_internet_speed
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WinDiag AI",
    page_icon="🖥️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:

    st.session_state.thread_id = "streamlit-user-1"


if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🖥️ WinDiag AI")

    st.caption(
        "Windows Diagnostic Assistant"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "💬 AI Chat",
            "🖥️ System",
            "📊 Monitor",
            "📚 Knowledge",
            "⚙️ Settings"
        ]
    )

    st.divider()

    st.caption(
        "WinDiag AI v1.0"
    )


# ============================================================
# AI CHAT PAGE
# ============================================================

if page == "💬 AI Chat":

    st.title("💬 AI Diagnostic Chat")

    st.write(
        "Describe a Windows problem and I'll help diagnose it."
    )


    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    prompt = st.chat_input(
        "Describe your Windows problem..."
    )


    # ========================================================
    # PROCESS MESSAGE
    # ========================================================

    if prompt:

        # ----------------------------------------------------
        # STORE USER MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })


        # ----------------------------------------------------
        # DISPLAY USER MESSAGE
        # ----------------------------------------------------

        with st.chat_message("user"):

            st.markdown(prompt)


        # ----------------------------------------------------
        # RUN BACKEND
        # ----------------------------------------------------

        try:

            with st.chat_message("assistant"):

                with st.spinner(
                    "Analyzing your system..."
                ):

                    result = run_diagnostic(
                        query=prompt,
                        thread_id=st.session_state.thread_id
                    )


                # ------------------------------------------------
                # GET ROUTE
                # ------------------------------------------------

                route = result["route"]


                # ------------------------------------------------
                # DISPLAY ROUTE
                # ------------------------------------------------

                st.caption(
                    f"Route: {route}"
                )


                # ------------------------------------------------
                # DIAGNOSTIC / BOTH
                # ------------------------------------------------

                if route in ["DIAGNOSTIC", "BOTH"]:

                    response = (
                        result["structured_response"]
                    )


                    st.markdown(
                        "### Observed"
                    )

                    for item in response.observed:

                        st.markdown(
                            f"- {item}"
                        )


                    st.markdown(
                        "### Possible Contributors"
                    )

                    for item in (
                        response.possible_contributors
                    ):

                        st.markdown(
                            f"- {item}"
                        )


                    st.markdown(
                        "### Confirmed Findings"
                    )

                    for item in (
                        response.confirmed_findings
                    ):

                        st.markdown(
                            f"- {item}"
                        )


                    st.markdown(
                        "### Recommendations"
                    )

                    for item in (
                        response.recommendations
                    ):

                        st.markdown(
                            f"- {item}"
                        )


                # ------------------------------------------------
                # KNOWLEDGE
                # ------------------------------------------------

                else:

                    st.markdown(
                        result["raw_response"]
                    )


            # ====================================================
            # PREPARE RESPONSE FOR CHAT HISTORY
            # ====================================================

            if route in ["DIAGNOSTIC", "BOTH"]:

                response = (
                    result["structured_response"]
                )


                response_text = (
                    "### Observed\n"
                    + "\n".join(
                        f"- {item}"
                        for item in response.observed
                    )
                    + "\n\n### Possible Contributors\n"
                    + "\n".join(
                        f"- {item}"
                        for item in (
                            response.possible_contributors
                        )
                    )
                    + "\n\n### Confirmed Findings\n"
                    + "\n".join(
                        f"- {item}"
                        for item in (
                            response.confirmed_findings
                        )
                    )
                    + "\n\n### Recommendations\n"
                    + "\n".join(
                        f"- {item}"
                        for item in response.recommendations
                    )
                )


            else:

                response_text = (
                    result["raw_response"]
                )


            # ====================================================
            # STORE ASSISTANT RESPONSE
            # ====================================================

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })


        # --------------------------------------------------------
        # ERROR HANDLING
        # --------------------------------------------------------

        except Exception as error:

            error_text = str(error)


            if (
                "HfHubHTTPError" in error_text
                or "500" in error_text
                or "502" in error_text
                or "503" in error_text
                or "504" in error_text
            ):

                error_message = (
                    "⚠️ **The AI model provider is "
                    "temporarily unavailable.**\n\n"
                    "Please try again in a moment."
                )

            else:

                error_message = (
                    "⚠️ **Something went wrong while "
                    "processing your request.**\n\n"
                    "Please try again."
                )


            with st.chat_message("assistant"):

                st.error(
                    error_message
                )


            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })


# ============================================================
# SYSTEM PAGE
# ============================================================

elif page == "🖥️ System":

    st.title("🖥️ System Overview")

    st.write(
        "Current information about your Windows computer."
    )


    # ========================================================
    # REFRESH BUTTON
    # ========================================================

    refresh = st.button(
        "🔄 Refresh System Information"
    )


    # ========================================================
    # GET SYSTEM INFORMATION
    # ========================================================

    try:

        cpu = get_cpu_usage.invoke({})

        memory = get_memory_usage.invoke({})

        disk = get_system_drive_storage.invoke({})

        system = get_system_info.invoke({})


        # ====================================================
        # SYSTEM INFORMATION
        # ====================================================

        st.subheader(
            "System Information"
        )


        # ----------------------------------------------------
        # Extract Windows information
        # ----------------------------------------------------

        if isinstance(system, dict):

            os_name = system.get(
                "os",
                system.get(
                    "system",
                    "Unknown"
                )
            )

            os_version = system.get(
                "version",
                "Unknown"
            )

            build = system.get(
                "build",
                "Unknown"
            )

        else:

            os_name = "Unknown"

            os_version = "Unknown"

            build = "Unknown"


        # ====================================================
        # SYSTEM INFO COLUMNS
        # ====================================================

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Operating System",
                os_name
            )


        with col2:

            st.metric(
                "Version",
                os_version
            )


        with col3:

            st.metric(
                "Build",
                build
            )


        st.divider()


        # ====================================================
        # RESOURCE USAGE
        # ====================================================

        st.subheader(
            "Resource Usage"
        )


        col1, col2, col3 = st.columns(3)


        # ----------------------------------------------------
        # CPU
        # ----------------------------------------------------

        with col1:

            st.metric(
                "CPU Usage",
                f"{cpu['usage_percent']}%"
            )

            st.caption(
                f"Physical cores: "
                f"{cpu['physical_cores']}"
            )

            st.caption(
                f"Logical processors: "
                f"{cpu['logical_processors']}"
            )


        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

        with col2:

            st.metric(
                "Memory Usage",
                f"{memory['usage_percent']}%"
            )

            st.caption(
                f"Used: "
                f"{memory['used_ram_gb']} GB"
            )

            st.caption(
                f"Available: "
                f"{memory['available_ram_gb']} GB"
            )


        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        with col3:

            st.metric(
                "System Drive",
                f"{disk}%"
            )

            st.caption(
                "C: drive capacity used"
            )


        st.divider()


        # ====================================================
        # PROCESSOR INFORMATION
        # ====================================================

        st.subheader(
            "Processor Information"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Physical Cores",
                cpu["physical_cores"]
            )


        with col2:

            st.metric(
                "Logical Processors",
                cpu["logical_processors"]
            )


        # ====================================================
        # REFRESH INFORMATION
        # ====================================================

        if refresh:

            st.success(
                "System information refreshed."
            )


    except Exception as error:

        st.error(
            "Unable to retrieve system information."
        )

        st.caption(
            str(error)
        )

# ============================================================
# MONITOR PAGE
# ============================================================

elif page == "📊 Monitor":

    st.title("📊 System Monitor")

    st.write(
        "Current resource usage, processes and network status."
    )


    # ========================================================
    # REFRESH
    # ========================================================

    if st.button("🔄 Refresh Monitor"):

        st.rerun()


    # ========================================================
    # GET SYSTEM SNAPSHOT
    # ========================================================

    try:

        snapshot = get_system_snapshot()

        cpu = snapshot["cpu"]

        memory = snapshot["memory"]

        disk = snapshot["disk"]

        processes = snapshot["processes"]

        network = snapshot["network"]


        # ====================================================
        # RESOURCE USAGE
        # ====================================================

        st.subheader("Resource Usage")

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "CPU Usage",
                f"{cpu['usage_percent']}%"
            )


        with col2:

            st.metric(
                "Memory Usage",
                f"{memory['usage_percent']}%"
            )


        with col3:

            st.metric(
                "System Drive",
                f"{disk}%"
            )


        st.divider()


        # ====================================================
        # TOP PROCESSES
        # ====================================================

        st.subheader("Top CPU Processes")


        if processes:

            process_rows = []

            for process in processes:

                process_rows.append({
                    "Process": process["name"],
                    "PID": process["pid"],
                    "CPU %": process["cpu_percent"],
                    "Memory %": process["memory_percent"]
                })


            st.dataframe(
                process_rows,
                hide_index=True
            )

        else:

            st.info(
                "No process information available."
            )


        st.divider()


        # ====================================================
        # NETWORK STATUS
        # ====================================================

        st.subheader("🌐 Network Status")


        if isinstance(network, dict):

            interfaces = network.get(
                "interfaces",
                {}
            )

            interface_status = network.get(
                "interface_status",
                {}
            )

            local_network_test = network.get(
                "local_network_test",
                {}
            )


            # ------------------------------------------------
            # FIND ACTIVE INTERFACE
            # ------------------------------------------------

            active_interface = None

            for name, status in interface_status.items():

                if status.get("is_up"):

                    if name != "Loopback Pseudo-Interface 1":

                        active_interface = name

                        break


            if active_interface:

                st.success(
                    f"Connected through {active_interface}"
                )

                active_addresses = interfaces.get(
                    active_interface,
                    []
                )

                ip_address = "Unavailable"

                for address in active_addresses:

                    if address.get("address"):

                        ip = address["address"]

                        if "." in ip and not ip.startswith(
                            "169.254."
                        ):

                            ip_address = ip

                            break


                status = interface_status.get(
                    active_interface,
                    {}
                )

                link_speed = status.get(
                    "link_speed_mbps",
                    "Unknown"
                )


                col1, col2 = st.columns(2)


                with col1:

                    st.metric(
                        "IP Address",
                        ip_address
                    )


                with col2:

                    st.metric(
                        "Wi-Fi Link Speed",
                        f"{link_speed} Mbps"
                    )


            else:

                st.warning(
                    "No active network interface detected."
                )


            # ------------------------------------------------
            # LOCAL NETWORK TEST
            # ------------------------------------------------

            st.markdown(
                "#### Local Network Quality"
            )


            gateway = local_network_test.get(
                "gateway",
                "Unavailable"
            )

            latency = local_network_test.get(
                "latency_ms",
                "Unavailable"
            )

            packet_loss = local_network_test.get(
                "packet_loss_percent",
                "Unavailable"
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Gateway",
                    gateway
                )


            with col2:

                st.metric(
                    "Gateway Latency",
                    f"{latency} ms"
                )


            with col3:

                st.metric(
                    "Packet Loss",
                    f"{packet_loss}%"
                )


            st.caption(
                "Wi-Fi link speed is the adapter's reported "
                "connection speed, not Internet speed."
            )


        else:

            st.info(
                "Network information unavailable."
            )


        st.divider()


        # ====================================================
        # INTERNET SPEED TEST
        # ====================================================

        st.subheader(
            "🌐 Internet Speed Test"
        )

        st.caption(
            "Runs an on-demand Ookla speed test. "
            "This may take a few seconds."
        )


        if st.button(
            "🚀 Run Internet Speed Test"
        ):

            with st.spinner(
                "Testing Internet speed..."
            ):

                speed_result =test_internet_speed.invoke({})


            if isinstance(speed_result, dict):

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Download",
                        f"{speed_result.get('download_mbps', 'N/A')} Mbps"
                    )


                with col2:

                    st.metric(
                        "Upload",
                        f"{speed_result.get('upload_mbps', 'N/A')} Mbps"
                    )


                with col3:

                    st.metric(
                        "Latency",
                        f"{speed_result.get('latency_ms', 'N/A')} ms"
                    )


                col1, col2 = st.columns(2)


                with col1:

                    st.metric(
                        "Jitter",
                        f"{speed_result.get('jitter_ms', 'N/A')} ms"
                    )


                with col2:

                    st.metric(
                        "Packet Loss",
                        f"{speed_result.get('packet_loss_percent', 'N/A')}%"
                    )


            else:

                st.write(
                    speed_result
                )


    except Exception as error:

        st.error(
            "Unable to retrieve monitoring information."
        )

        st.caption(
            str(error)
        )

# ============================================================
# KNOWLEDGE PAGE
# ============================================================

elif page == "📚 Knowledge":

    st.title("📚 Windows Knowledge")

    st.write(
        "Windows troubleshooting knowledge base."
    )

    st.info(
        "Knowledge explorer will be added later."
    )


# ============================================================
# SETTINGS PAGE
# ============================================================
# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.write(
        "Manage your WinDiag AI session."
    )


    # ========================================================
    # CONVERSATION
    # ========================================================

    st.subheader("Conversation")


    if st.button(
        "🆕 Start New Conversation"
    ):

        import uuid

        st.session_state.thread_id = (
            f"streamlit-user-{uuid.uuid4()}"
        )

        st.session_state.messages = []

        st.success(
            "New conversation started."
        )

        st.rerun()


    if st.button(
        "🗑️ Clear Chat"
    ):

        st.session_state.messages = []

        st.success(
            "Chat history cleared."
        )

        st.rerun()


    st.divider()


    # ========================================================
    # ABOUT
    # ========================================================

    st.subheader("About WinDiag AI")

    st.write(
        """
        **WinDiag AI** is an AI-powered Windows diagnostic
        assistant that combines:

        - Windows troubleshooting knowledge
        - Retrieval-Augmented Generation (RAG)
        - Chroma vector database
        - Query rewriting
        - Document reranking
        - Windows system diagnostic tools
        - LangChain agents
        - Conversation memory
        """
    )


    st.divider()


    st.caption(
        "WinDiag AI v1.0"
    )