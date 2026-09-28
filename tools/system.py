import platform
import psutil

from langchain_core.tools import tool


# ============================================================
# SYSTEM INFORMATION TOOL
# ============================================================

@tool
def get_system_info() -> dict:
    """
    Get basic Windows operating system and hardware information.
    """

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True),
        "total_ram_gb": round(
            psutil.virtual_memory().total / (1024 ** 3),
            2
        )
    }


# ============================================================
# TEST THE TOOL
# ============================================================

if __name__ == "__main__":

    print("Tool name:", get_system_info.name)

    print("Tool description:", get_system_info.description)

    print("Tool arguments:", get_system_info.args)

    print("Tool type:", type(get_system_info))

    print("\nTool result:")

    result = get_system_info.invoke({})

    for key, value in result.items():
        print(f"{key}: {value}")