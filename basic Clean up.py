import os
import tempfile
import shutil
import ctypes
import platform
import logging
import time
import argparse
from datetime import datetime
from pathlib import Path
import sys

class CleanupManager:
    def __init__(self, dry_run=False, log_file=None, min_age_hours=0):
        """
        Initialize the cleanup manager.
        
        Args:
            dry_run (bool): If True, only simulate deletions
            log_file (str): Path to log file, if None logs to stdout
            min_age_hours (int): Minimum age of files to delete in hours
        """
        self.dry_run = dry_run
        self.min_age_hours = min_age_hours
        self.bytes_cleaned = 0
        self.files_cleaned = 0
        
        # Setup logging
        self.setup_logging(log_file)
        
        # Additional temp directories based on OS
        self.temp_dirs = [tempfile.gettempdir()]
        if platform.system() == 'Windows':
            self.temp_dirs.extend([
                os.path.expandvars('%WINDIR%\\Temp'),
                os.path.expandvars('%LOCALAPPDATA%\\Temp')
            ])
        elif platform.system() == 'Darwin':  # macOS
            self.temp_dirs.append('/private/tmp')
        
    def setup_logging(self, log_file):
        """Configure logging system."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        if log_file:
            logging.basicConfig(
                level=logging.INFO,
                format=log_format,
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(level=logging.INFO, format=log_format)

    def is_safe_to_delete(self, path):
        """
        Check if it's safe to delete the file/directory.
        
        Args:
            path (str): Path to check
            
        Returns:
            bool: True if safe to delete
        """
        # Check if file/directory is old enough
        if self.min_age_hours > 0:
            try:
                mtime = os.path.getmtime(path)
                age_hours = (time.time() - mtime) / 3600
                if age_hours < self.min_age_hours:
                    return False
            except OSError:
                return False

        # List of critical directories/files to never delete
        critical_patterns = [
            'System32', 'Windows', 'Program Files',
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys'
        ]
        
        return not any(pattern.lower() in str(path).lower() 
                      for pattern in critical_patterns)

    def get_size(self, path):
        """Get size of file or directory."""
        try:
            if os.path.isfile(path) or os.path.islink(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total_size = 0
                for dirpath, _, filenames in os.walk(path):
                    for fname in filenames:
                        file_path = os.path.join(dirpath, fname)
                        if os.path.exists(file_path):  # Check if file still exists
                            total_size += os.path.getsize(file_path)
                return total_size
        except (OSError, PermissionError):
            return 0
        return 0

    def delete_temp_files(self):
        """Delete temporary files from all temporary directories."""
        for temp_dir in self.temp_dirs:
            if not os.path.exists(temp_dir):
                logging.warning(f"Temporary directory not found: {temp_dir}")
                continue
                
            logging.info(f"Cleaning directory: {temp_dir}")
            
            for item in os.scandir(temp_dir):
                try:
                    if not self.is_safe_to_delete(item.path):
                        continue
                        
                    size = self.get_size(item.path)
                    
                    if self.dry_run:
                        logging.info(f"Would delete: {item.path} ({size/1024/1024:.2f} MB)")
                        continue
                        
                    if item.is_file() or item.is_symlink():
                        os.unlink(item.path)
                        logging.info(f"Deleted file: {item.path} ({size/1024/1024:.2f} MB)")
                    elif item.is_dir():
                        shutil.rmtree(item.path, ignore_errors=True)
                        logging.info(f"Deleted directory: {item.path} ({size/1024/1024:.2f} MB)")
                        
                    self.bytes_cleaned += size
                    self.files_cleaned += 1
                        
                except Exception as e:
                    logging.error(f"Error processing {item.path}: {str(e)}")

    def clear_recycle_bin(self):
        """Clear the system recycle bin/trash."""
        if self.dry_run:
            logging.info("Would clear recycle bin")
            return
            
        try:
            if platform.system() == 'Windows':
                result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
                if result == 0:
                    logging.info("Recycle Bin cleared successfully")
                else:
                    logging.error(f"Failed to clear Recycle Bin. Error code: {result}")
            elif platform.system() == 'Darwin':  # macOS
                trash_dir = os.path.expanduser("~/.Trash")
                if os.path.exists(trash_dir):
                    shutil.rmtree(trash_dir, ignore_errors=True)
                    logging.info("Trash cleared successfully")
            elif platform.system() == 'Linux':
                trash_dir = os.path.expanduser("~/.local/share/Trash")
                if os.path.exists(trash_dir):
                    shutil.rmtree(trash_dir, ignore_errors=True)
                    logging.info("Trash cleared successfully")
            else:
                logging.warning("Recycle bin clearing not implemented for this OS")
        except Exception as e:
            logging.error(f"Error clearing recycle bin: {str(e)}")

    def generate_report(self):
        """Generate a cleanup report."""
        report = f"""
Cleanup Report
-------------
Time: {datetime.now()}
Mode: {'Dry run' if self.dry_run else 'Active'}
Files processed: {self.files_cleaned}
Total space cleaned: {self.bytes_cleaned/1024/1024:.2f} MB
Temporary directories cleaned:
{chr(10).join(f'- {d}' for d in self.temp_dirs)}
"""
        logging.info(report)
        return report

def main():
    parser = argparse.ArgumentParser(description='System Cleanup Utility')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simulate cleanup without deleting files')
    parser.add_argument('--log-file', type=str, 
                        help='Path to log file (optional)')
    parser.add_argument('--min-age', type=int, default=0,
                        help='Minimum age of files to delete (hours)')
    parser.add_argument('--skip-recycle-bin', action='store_true',
                        help='Skip clearing the recycle bin')
    
    args = parser.parse_args()
    
    try:
        # Check for admin rights on Windows
        if platform.system() == 'Windows' and not ctypes.windll.shell32.IsUserAnAdmin():
            logging.warning("Running without administrator privileges. Some operations may fail.")
        
        cleanup_manager = CleanupManager(
            dry_run=args.dry_run,
            log_file=args.log_file,
            min_age_hours=args.min_age
        )
        
        cleanup_manager.delete_temp_files()
        
        if not args.skip_recycle_bin:
            cleanup_manager.clear_recycle_bin()
            
        cleanup_manager.generate_report()
        
    except KeyboardInterrupt:
        logging.info("\nCleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()