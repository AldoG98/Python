import platform
import psutil
import os
import time
from datetime import datetime
from tabulate import tabulate
import subprocess
import ctypes
import sys

def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_gpu_info_windows():
    """Get GPU information using Windows Management Instrumentation Command-line"""
    try:
        gpu_info = []
        wmic_cmd = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", 
                                          "name,driverversion,videoprocessor,adapterram"], 
                                         stderr=subprocess.STDOUT).decode()
        
        # Parse the output
        lines = [line.strip() for line in wmic_cmd.split('\n') if line.strip()]
        if len(lines) > 1:  # First line is headers
            gpu_details = lines[1:]
            for gpu in gpu_details:
                if gpu.strip():
                    gpu_info.extend([
                        ["GPU Name", gpu.split('  ')[0].strip()],
                        ["", ""]
                    ])
        return gpu_info
    except:
        return []

def get_cpu_temp():
    """Get CPU temperature using platform-specific methods"""
    try:
        if platform.system() == 'Windows':
            # Try using OpenHardwareMonitor via a command-line alternative
            cmd = "wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature"
            output = subprocess.check_output(cmd.split()).decode()
            try:
                temp = float(output.split('\n')[1]) / 10.0 - 273.15  # Convert from decikelvin to Celsius
                return [["CPU Temperature", f"{temp:.1f}°C"]]
            except:
                return []
    except:
        return []
    return []

def get_detailed_cpu_info():
    """Get detailed CPU information"""
    cpu_info = []
    
    # Get CPU brand
    try:
        cpu_brand = subprocess.check_output(["wmic", "cpu", "get", "name"], 
                                          stderr=subprocess.STDOUT).decode()
        cpu_brand = cpu_brand.split('\n')[1].strip()
        cpu_info.append(["CPU Model", cpu_brand])
    except:
        pass

    # Basic CPU info
    cpu_info.extend([
        ["Physical Cores", psutil.cpu_count(logical=False)],
        ["Total Cores", psutil.cpu_count(logical=True)],
        ["CPU Usage %", f"{psutil.cpu_percent(interval=1)}%"]
    ])
    
    # CPU Frequencies
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info.extend([
                ["Max Frequency", f"{cpu_freq.max:.2f}MHz"],
                ["Min Frequency", f"{cpu_freq.min:.2f}MHz"],
                ["Current Frequency", f"{cpu_freq.current:.2f}MHz"]
            ])
    except:
        pass

    # CPU load average
    try:
        load_avg = psutil.getloadavg()
        cpu_info.extend([
            ["Load Average (1 min)", f"{load_avg[0]:.2f}"],
            ["Load Average (5 min)", f"{load_avg[1]:.2f}"],
            ["Load Average (15 min)", f"{load_avg[2]:.2f}"]
        ])
    except:
        pass

    return cpu_info

def get_pc_info():
    try:
        # Check for admin rights
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() if platform.system() == 'Windows' else False
        if not is_admin:
            print("Note: Running without administrator privileges. Some information may be limited.\n")

        # System Information
        print("="*40, "System Information", "="*40)
        uname = platform.uname()
        system_info = [
            ["OS", f"{uname.system} {platform.win32_edition()}" if platform.system() == 'Windows' else uname.system],
            ["OS Version", uname.version],
            ["OS Release", uname.release],
            ["Architecture", uname.machine],
            ["Processor", uname.processor],
            ["Computer Name", uname.node],
            ["Boot Time", datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")],
            ["System Uptime", str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]]
        ]
        print(tabulate(system_info, headers=["Component", "Value"], tablefmt="grid"))

        # CPU Information
        print("\n", "="*40, "CPU Information", "="*40)
        cpu_info = get_detailed_cpu_info()
        print(tabulate(cpu_info, headers=["CPU Property", "Value"], tablefmt="grid"))

        # Temperature Information
        temp_info = get_cpu_temp()
        if temp_info:
            print("\n", "="*40, "Temperature Information", "="*40)
            print(tabulate(temp_info, headers=["Sensor", "Temperature"], tablefmt="grid"))

        # GPU Information
        gpu_info = get_gpu_info_windows()
        if gpu_info:
            print("\n", "="*40, "GPU Information", "="*40)
            print(tabulate(gpu_info, headers=["GPU Property", "Value"], tablefmt="grid"))

        # Memory Information with Performance Counter
        print("\n", "="*40, "Memory Information", "="*40)
        virtual_mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = [
            ["Total Memory", get_size(virtual_mem.total)],
            ["Available Memory", get_size(virtual_mem.available)],
            ["Used Memory", get_size(virtual_mem.used)],
            ["Memory Usage", f"{virtual_mem.percent}%"],
            ["Memory Performance", f"{(virtual_mem.used / virtual_mem.total) * 100:.1f}% utilized"],
            ["", ""],
            ["Total Swap", get_size(swap.total)],
            ["Free Swap", get_size(swap.free)],
            ["Used Swap", get_size(swap.used)],
            ["Swap Usage", f"{swap.percent}%"]
        ]
        print(tabulate(memory_info, headers=["Memory Property", "Value"], tablefmt="grid"))

        # Enhanced Disk Information
        print("\n", "="*40, "Disk Information", "="*40)
        disk_info = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.extend([
                    ["Drive", partition.device],
                    ["Mount Point", partition.mountpoint],
                    ["File System", partition.fstype],
                    ["Total Size", get_size(partition_usage.total)],
                    ["Used Space", get_size(partition_usage.used)],
                    ["Free Space", get_size(partition_usage.free)],
                    ["Usage", f"{partition_usage.percent}%"],
                    ["Performance", f"{(partition_usage.used / partition_usage.total) * 100:.1f}% utilized"],
                    ["", ""]
                ])
            except Exception as e:
                continue
        
        print(tabulate(disk_info, headers=["Disk Property", "Value"], tablefmt="grid"))

        # Enhanced Disk I/O Information
        print("\n", "="*40, "Disk I/O Information", "="*40)
        disk_io = psutil.disk_io_counters(perdisk=True)
        io_info = []
        for disk, counters in disk_io.items():
            # Calculate actual current speeds
            time.sleep(1)  # Wait 1 second to measure current speed
            new_counters = psutil.disk_io_counters(perdisk=True)[disk]
            read_speed = get_size(new_counters.read_bytes - counters.read_bytes) + "/s"
            write_speed = get_size(new_counters.write_bytes - counters.write_bytes) + "/s"
            
            io_info.extend([
                ["Disk", disk],
                ["Total Read", get_size(counters.read_bytes)],
                ["Total Written", get_size(counters.write_bytes)],
                ["Current Read Speed", read_speed],
                ["Current Write Speed", write_speed],
                ["Read Operations", counters.read_count],
                ["Write Operations", counters.write_count],
                ["", ""]
            ])
        
        print(tabulate(io_info, headers=["I/O Property", "Value"], tablefmt="grid"))

        # Enhanced Network Information
        print("\n", "="*40, "Network Information", "="*40)
        network_info = []
        net_io = psutil.net_io_counters()
        
        # Get current speeds
        time.sleep(1)  # Wait 1 second to measure current speed
        new_net_io = psutil.net_io_counters()
        upload_speed = get_size(new_net_io.bytes_sent - net_io.bytes_sent) + "/s"
        download_speed = get_size(new_net_io.bytes_recv - net_io.bytes_recv) + "/s"
        
        network_info.extend([
            ["Total Sent", get_size(net_io.bytes_sent)],
            ["Total Received", get_size(net_io.bytes_recv)],
            ["Current Upload Speed", upload_speed],
            ["Current Download Speed", download_speed],
            ["Packets Sent", net_io.packets_sent],
            ["Packets Received", net_io.packets_recv],
            ["", ""]
        ])

        # Add interface information
        network_interfaces = psutil.net_if_addrs()
        for interface_name, interface_addresses in network_interfaces.items():
            for addr in interface_addresses:
                if str(addr.family) == 'AddressFamily.AF_INET':
                    network_info.extend([
                        ["Interface", interface_name],
                        ["IP Address", addr.address],
                        ["Netmask", addr.netmask],
                        ["Broadcast", addr.broadcast if hasattr(addr, 'broadcast') else "N/A"],
                        ["", ""]
                    ])
        
        print(tabulate(network_info, headers=["Network Property", "Value"], tablefmt="grid"))

        # Enhanced Process Information
        print("\n", "="*40, "Top Processes", "="*40)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                process_info = proc.info
                # Calculate process uptime
                uptime = datetime.now() - datetime.fromtimestamp(process_info['create_time'])
                processes.append([
                    process_info['name'],
                    process_info['pid'],
                    f"{process_info['cpu_percent']}%",
                    f"{process_info['memory_percent']:.1f}%",
                    str(uptime).split('.')[0]  # Process uptime
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by memory usage and get top processes
        processes.sort(key=lambda x: float(x[3].strip('%')), reverse=True)
        print(tabulate(processes[:10], 
                      headers=["Process Name", "PID", "CPU Usage", "Memory Usage", "Uptime"],
                      tablefmt="grid"))

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Gathering system information... Please wait while we collect real-time metrics.\n")
    get_pc_info()