import winreg
import os
import shutil
import subprocess

def scan_directory(directory_path):
    programs = []
    files = []
    directories = []
    
    for root, dirs, filenames in os.walk(directory_path):
        for dir in dirs:
            directories.append(os.path.join(root, dir))
        for file in filenames:
            file_path = os.path.join(root, file)
            if file.endswith('.exe'):
                program_info = get_program_info(file_path)
                if program_info:
                    programs.append(program_info)
            files.append(file_path)
    
    return programs, files, directories

def get_program_info(program_path):
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        if program_path.lower() in install_location.lower():
                            uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                            return {
                                "name": display_name,
                                "location": install_location,
                                "path": program_path,
                                "uninstall_string": uninstall_string
                            }
                    except FileNotFoundError:
                        continue
    except Exception as e:
        print(f"An error occurred while getting program info: {e}")
    
    return None

def uninstall_program(program):
    print(f"Uninstalling: {program['name']}")
    try:
        subprocess.run(program['uninstall_string'], shell=True, check=True)
        print(f"Successfully uninstalled {program['name']}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to uninstall {program['name']}. Error: {e}")

def delete_item(path):
    print(f"Deleting: {path}")
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Deleted directory and all its contents: {path}")
    except Exception as e:
        print(f"Failed to delete {path}. Error: {e}")

def display_menu(programs, files, directories):
    print("\nFound items:")
    for i, program in enumerate(programs, 1):
        print(f"P{i}. Program: {program['name']} (Located at: {program['location']})")
    for i, file in enumerate(files, 1):
        print(f"F{i}. File: {file}")
    for i, directory in enumerate(directories, 1):
        print(f"D{i}. Directory: {directory}")

def get_user_selection(programs, files, directories):
    to_process = []
    while True:
        choice = input("\nEnter item to process (e.g., P1, F2, D3), or 'done' to finish selection: ")
        if choice.lower() == 'done':
            break
        try:
            item_type, index = choice[0].upper(), int(choice[1:]) - 1
            if item_type == 'P' and 0 <= index < len(programs):
                to_process.append(('program', programs[index]))
            elif item_type == 'F' and 0 <= index < len(files):
                to_process.append(('file', files[index]))
            elif item_type == 'D' and 0 <= index < len(directories):
                to_process.append(('directory', directories[index]))
            else:
                print("Invalid selection. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input format. Please use 'P1', 'F2', 'D3', etc.")
    return to_process

def process_items(to_process):
    for item_type, item in to_process:
        if item_type == 'program':
            uninstall_program(item)
        elif item_type in ['file', 'directory']:
            delete_item(item)

def main():
    directory_to_scan = r"C:\Users\aldog\OneDrive\Desktop\Uninstall"
    
    print(f"Scanning directory: {directory_to_scan}")
    programs, files, directories = scan_directory(directory_to_scan)
    
    display_menu(programs, files, directories)
    
    to_process = get_user_selection(programs, files, directories)
    
    if to_process:
        confirm = input("\nAre you sure you want to proceed with the selected actions? (y/n): ")
        if confirm.lower() == 'y':
            process_items(to_process)
            print("All selected actions completed.")
        else:
            print("Actions cancelled.")
    else:
        print("No items selected for processing.")

if __name__ == "__main__":
    main()
