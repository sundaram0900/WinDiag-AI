import time
import psutil

from langchain_core.tools import tool


@tool
def get_top_processes() -> list:
    """
    Get the top 10 processes currently using CPU resources,
    along with their CPU and memory usage percentages.
    """

    processes = []

    # ========================================================
    # 1. START CPU MEASUREMENTS
    # ========================================================

    for process in psutil.process_iter():

        try:
            process.cpu_percent(None)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    # ========================================================
    # 2. MEASURE CPU USAGE OVER 1 SECOND
    # ========================================================

    time.sleep(1)

    # ========================================================
    # 3. GET CPU AND MEMORY INFORMATION
    # ========================================================

    for process in psutil.process_iter(
        ["name", "cpu_percent", "memory_percent"]
    ):

        try:
            info = process.info

            # Ignore Windows CPU idle pseudo-process
            if info["name"] == "System Idle Process":
                continue

            processes.append({
                "name": info["name"],
                "pid": process.pid,
                "cpu_percent": round(
                    info["cpu_percent"] / psutil.cpu_count(logical=True),
                    2
                ),
                "memory_percent": round(info["memory_percent"], 2)
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    # ========================================================
    # 4. SORT BY CPU USAGE
    # ========================================================

    processes.sort(
        key=lambda process: process["cpu_percent"],
        reverse=True
    )

    # ========================================================
    # 5. RETURN TOP 10 PROCESSES
    # ========================================================

    return processes[:10]


# ============================================================
# TEST THE TOOL DIRECTLY
# ============================================================

if __name__ == "__main__":

    print("Tool name:", get_top_processes.name)

    print("Tool description:", get_top_processes.description)

    print("Tool arguments:", get_top_processes.args)

    print("Tool type:", type(get_top_processes))

    print("\nTool result:")

    result = get_top_processes.invoke({})

    for process in result:
        print(process)