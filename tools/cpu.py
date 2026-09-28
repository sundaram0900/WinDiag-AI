import psutil

from langchain_core.tools import tool


@tool
def get_cpu_usage() -> dict:
    """
    Get current CPU usage and processor information from the
    Windows computer.
    """

    cpu_usage = psutil.cpu_percent(interval=1)

    frequency = psutil.cpu_freq()

    return {
        "usage_percent": cpu_usage,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True),
        "current_frequency_mhz": (
            round(frequency.current, 2)
            if frequency
            else None
        )
    }


if __name__ == "__main__":

    print("Tool name:", get_cpu_usage.name)

    print("Tool description:", get_cpu_usage.description)

    print("Tool arguments:", get_cpu_usage.args)

    print("Tool type:", type(get_cpu_usage))

    print("\nTool result:")

    result = get_cpu_usage.invoke({})

    print(result)