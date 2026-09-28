from tools.cpu import get_cpu_usage
from tools.memory import get_memory_usage
from tools.disk import get_system_drive_storage
from tools.process import get_top_processes
from tools.get_network_info import get_network_info


def get_system_snapshot():

    cpu = get_cpu_usage.invoke({})

    memory = get_memory_usage.invoke({})

    disk = get_system_drive_storage.invoke({})

    processes = get_top_processes.invoke({})

    network = get_network_info.invoke({})

    return {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "processes": processes,
        "network": network
    }