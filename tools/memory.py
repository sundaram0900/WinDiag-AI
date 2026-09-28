import psutil

from langchain_core.tools import tool


@tool
def get_memory_usage() -> dict:
    """
    Get current RAM usage information from the Windows computer,
    including total, used, available memory and usage percentage.
    """

    memory = psutil.virtual_memory()

    return {
        "total_ram_gb": round(memory.total / (1024 ** 3), 2),
        "used_ram_gb": round(memory.used / (1024 ** 3), 2),
        "available_ram_gb": round(memory.available / (1024 ** 3), 2),
        "usage_percent": memory.percent
    }


if __name__ == "__main__":

    print("Tool name:", get_memory_usage.name)

    print("Tool description:", get_memory_usage.description)

    print("Tool arguments:", get_memory_usage.args)

    print("Tool type:", type(get_memory_usage))

    print("\nTool result:")

    result = get_memory_usage.invoke({})

    print(result)