import psutil

from langchain_core.tools import tool


# ============================================================
# SYSTEM DRIVE STORAGE TOOL
# ============================================================

@tool
def get_system_drive_storage() -> float:
    """
    Get the percentage of storage capacity currently used
    on the Windows system drive (C:).
    """

    disk = psutil.disk_usage("C:\\")

    return disk.percent


# ============================================================
# TEST THE TOOL
# ============================================================

if __name__ == "__main__":

    print("Tool name:", get_system_drive_storage.name)

    print("Tool description:", get_system_drive_storage.description)

    print("Tool arguments:", get_system_drive_storage.args)

    print("Tool type:", type(get_system_drive_storage))

    print("\nTool result:")

    result = get_system_drive_storage.invoke({})

    print("C: drive storage used:", result, "%")