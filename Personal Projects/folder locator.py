import os

def locate_football_manager_folder():
    # Common directories to check for Football Manager
    common_paths = [
        os.path.expanduser('~\\Documents\\Sports Interactive'),  # Standard location in Documents
        os.path.expanduser('~\\Documents'),                      # General Documents folder
        os.path.expanduser('~\\AppData\\Local'),                 # Local AppData folder
        os.path.expanduser('~\\AppData\\Roaming'),               # Roaming AppData folder
        'C:\\Program Files (x86)\\Steam\\steamapps\\common',     # Steam default directory
        'C:\\Program Files\\Steam\\steamapps\\common',           # Alternative Steam directory
    ]

    for path in common_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if 'Football Manager' in dirs or any('Football Manager' in d for d in dirs):
                    full_path = os.path.join(root, 'Football Manager')
                    print(f"Football Manager folder found: {full_path}")
                    return full_path

    print("Football Manager folder not found.")
    return None

if __name__ == "__main__":
    locate_football_manager_folder()
