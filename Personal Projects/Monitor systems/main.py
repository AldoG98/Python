import platform
from datetime import datetime
import GPUtil
import socket
import wmi
import psutil

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def system_info():
    # System Information
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")

    # Initialize WMI
    w = wmi.WMI()

    # Boot Time
    print("="*40, "Boot Time", "="*40)
    try:
        boot_time = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time)
        print(f"Boot Time: {bt.strftime('%Y/%m/%d %H:%M:%S')}")
    except:
        try:
            for os in w.Win32_OperatingSystem():
                print(f"Last Boot Time: {os.LastBootUpTime}")
        except:
            print("Boot time information unavailable")

    # CPU Info
    print("="*40, "CPU Info", "="*40)
    try:
        cpu_info = w.Win32_Processor()[0]
        print(f"Physical cores: {psutil.cpu_count(logical=False)}")
        print(f"Total cores: {psutil.cpu_count(logical=True)}")
        print(f"Processor Name: {cpu_info.Name.strip()}")
        print(f"Max Clock Speed: {cpu_info.MaxClockSpeed} MHz")
        print(f"Current Load: {cpu_info.LoadPercentage}%")

        # CPU Usage per core
        print("\nCPU Usage Per Core:")
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            print(f"Core {i}: {percentage}%")
        print(f"Total CPU Usage: {psutil.cpu_percent()}%")
    except Exception as e:
        print(f"Could not retrieve complete CPU information: {str(e)}")

    # Memory Information
    print("="*40, "Memory Information", "="*40)
    try:
        virtual_memory = psutil.virtual_memory()
        print(f"Total: {get_size(virtual_memory.total)}")
        print(f"Available: {get_size(virtual_memory.available)}")
        print(f"Used: {get_size(virtual_memory.used)}")
        print(f"Percentage: {virtual_memory.percent}%")
    except:
        try:
            os_info = w.Win32_OperatingSystem()[0]
            total_memory = int(os_info.TotalVisibleMemorySize) * 1024
            free_memory = int(os_info.FreePhysicalMemory) * 1024
            used_memory = total_memory - free_memory
            memory_percent = (used_memory / total_memory) * 100
            print(f"Total: {get_size(total_memory)}")
            print(f"Available: {get_size(free_memory)}")
            print(f"Used: {get_size(used_memory)}")
            print(f"Percentage: {memory_percent:.1f}%")
        except:
            print("Memory information unavailable")

    # Disk Information
    print("="*40, "Disk Information", "="*40)
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                print(f"=== Device: {partition.device} ===")
                print(f"  Mountpoint: {partition.mountpoint}")
                print(f"  File system type: {partition.fstype}")
                print(f"  Total Size: {get_size(partition_usage.total)}")
                print(f"  Used: {get_size(partition_usage.used)}")
                print(f"  Free: {get_size(partition_usage.free)}")
                print(f"  Percentage: {partition_usage.percent}%")
            except PermissionError:
                continue
    except:
        try:
            for disk in w.Win32_LogicalDisk(DriveType=3):
                print(f"=== Drive: {disk.Caption} ===")
                print(f"  File System: {disk.FileSystem}")
                print(f"  Total Size: {get_size(int(disk.Size))}")
                print(f"  Free Space: {get_size(int(disk.FreeSpace))}")
                used_space = int(disk.Size) - int(disk.FreeSpace)
                print(f"  Used Space: {get_size(used_space)}")
                print(f"  Usage: {(used_space/int(disk.Size))*100:.1f}%")
        except:
            print("Disk information unavailable")

    # Network Information
    print("="*40, "Network Information", "="*40)
    try:
        # Get network interfaces
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            for addr in interface_addresses:
                if str(addr.family) == 'AddressFamily.AF_INET':
                    print(f"=== Interface: {interface_name} ===")
                    print(f"  IP Address: {addr.address}")
                    print(f"  Netmask: {addr.netmask}")
                    if addr.broadcast:
                        print(f"  Broadcast IP: {addr.broadcast}")
        
        # Get IO statistics
        net_io = psutil.net_io_counters()
        print("\nNetwork IO Statistics Since Boot:")
        print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
        print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    except:
        try:
            for interface in w.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                print(f"=== Interface: {interface.Description} ===")
                if interface.IPAddress:
                    print(f"  IP Address: {interface.IPAddress[0]}")
                if interface.IPSubnet:
                    print(f"  Subnet Mask: {interface.IPSubnet[0]}")
                if interface.DefaultIPGateway:
                    print(f"  Default Gateway: {interface.DefaultIPGateway[0]}")
        except:
            print("Network information unavailable")

    # GPU Information
    print("="*40, "GPU Information", "="*40)
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            print(f"GPU ID: {gpu.id}, Name: {gpu.name}")
            print(f"  Memory Total: {gpu.memoryTotal}MB")
            print(f"  Memory Used: {gpu.memoryUsed}MB")
            print(f"  Memory Free: {gpu.memoryFree}MB")
            print(f"  GPU Load: {gpu.load*100}%")
            print(f"  Temperature: {gpu.temperature} °C")
    except Exception as e:
        print(f"Could not retrieve GPU information: {e}")

if __name__ == "__main__":
    system_info()