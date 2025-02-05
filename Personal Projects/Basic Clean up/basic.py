import os
import tempfile
import shutil
import ctypes
import platform

def delete_temp_files():
    temp_dir = tempfile.gettempdir()
    print(f"Deleting files in temporary directory: {temp_dir}")
    
    # Loop through all files in the temp directory and delete them
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def clear_recycle_bin():
    print("Clearing Recycle Bin...")
    if platform.system() == 'Windows':
        # Use Windows API to clear Recycle Bin
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        print("Recycle Bin cleared.")
    else:
        print("This function is only implemented for Windows.")

def main():
    print("Starting clean sweep...")
    delete_temp_files()
    clear_recycle_bin()
    print("Clean sweep completed!")

if __name__ == "__main__":
    main()
