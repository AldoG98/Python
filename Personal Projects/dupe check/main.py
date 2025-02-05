import os
import hashlib
from pathlib import Path
import argparse
from datetime import datetime
import shutil
from typing import Dict, List, Set
import logging

class DuplicateFinder:
    def __init__(self, min_size: int = 1024):
        """
        Initialize DuplicateFinder with minimum file size to check (in bytes).
        
        Args:
            min_size: Minimum file size in bytes to consider (default: 1KB)
        """
        self.min_size = min_size
        self.duplicates: Dict[str, List[str]] = {}
        self.total_size_saved = 0
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def calculate_file_hash(self, filepath: str, chunk_size: int = 8192) -> str:
        """
        Calculate MD5 hash of a file in chunks to handle large files efficiently.
        
        Args:
            filepath: Path to the file
            chunk_size: Size of chunks to read (default: 8KB)
        Returns:
            str: MD5 hash of the file
        """
        md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    md5.update(chunk)
            return md5.hexdigest()
        except (IOError, OSError) as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
            return ""

    def find_duplicates(self, directory: str, extensions: Set[str] = None) -> Dict[str, List[str]]:
        """
        Find duplicate files in the specified directory.
        
        Args:
            directory: Directory to search for duplicates
            extensions: Set of file extensions to check (e.g., {'.jpg', '.png'})
        Returns:
            Dict mapping file hashes to lists of duplicate file paths
        """
        size_dict: Dict[int, List[str]] = {}
        
        # First pass: Group files by size
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                
                # Skip if extension doesn't match filter
                if extensions and not any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    continue
                
                try:
                    file_size = os.path.getsize(filepath)
                    if file_size >= self.min_size:
                        if file_size in size_dict:
                            size_dict[file_size].append(filepath)
                        else:
                            size_dict[file_size] = [filepath]
                except OSError as e:
                    self.logger.error(f"Error accessing {filepath}: {e}")

        # Second pass: Calculate hashes only for files with same size
        for size, filepaths in size_dict.items():
            if len(filepaths) > 1:
                for filepath in filepaths:
                    file_hash = self.calculate_file_hash(filepath)
                    if file_hash:
                        if file_hash in self.duplicates:
                            self.duplicates[file_hash].append(filepath)
                            self.total_size_saved += size
                        else:
                            self.duplicates[file_hash] = [filepath]

        # Remove entries without duplicates
        self.duplicates = {k: v for k, v in self.duplicates.items() if len(v) > 1}
        return self.duplicates

    def print_report(self) -> None:
        """Print a detailed report of found duplicates."""
        if not self.duplicates:
            print("No duplicates found!")
            return

        print("\n=== Duplicate Files Report ===")
        print(f"Total groups of duplicates: {len(self.duplicates)}")
        print(f"Total space that could be saved: {self.total_size_saved / (1024*1024):.2f} MB\n")

        for hash_value, file_list in self.duplicates.items():
            print(f"\nDuplicate group (Hash: {hash_value}):")
            size = os.path.getsize(file_list[0])
            print(f"Size: {size / 1024:.2f} KB")
            for idx, filepath in enumerate(file_list, 1):
                print(f"{idx}. {filepath}")
            print("-" * 80)

    def move_duplicates(self, destination: str) -> None:
        """
        Move duplicate files to a specified directory, organizing them by hash.
        
        Args:
            destination: Directory to move duplicates to
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = os.path.join(destination, f'duplicates_{timestamp}')
        
        for hash_value, file_list in self.duplicates.items():
            # Skip the first file (original)
            for filepath in file_list[1:]:
                try:
                    # Create hash directory
                    hash_dir = os.path.join(base_dir, hash_value[:8])
                    os.makedirs(hash_dir, exist_ok=True)
                    
                    # Move file
                    filename = os.path.basename(filepath)
                    shutil.move(filepath, os.path.join(hash_dir, filename))
                    self.logger.info(f"Moved {filepath} to duplicate folder")
                except OSError as e:
                    self.logger.error(f"Error moving {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Find and manage duplicate files')
    parser.add_argument('directory', help='Directory to scan for duplicates')
    parser.add_argument('--min-size', type=int, default=1024,
                       help='Minimum file size in bytes to consider (default: 1024)')
    parser.add_argument('--extensions', type=str, nargs='+',
                       help='File extensions to check (e.g., .jpg .png)')
    parser.add_argument('--move-to', type=str,
                       help='Move duplicates to specified directory')
    
    args = parser.parse_args()
    
    finder = DuplicateFinder(min_size=args.min_size)
    extensions = set(args.extensions) if args.extensions else None
    
    print(f"Scanning directory: {args.directory}")
    finder.find_duplicates(args.directory, extensions)
    finder.print_report()
    
    if args.move_to:
        finder.move_duplicates(args.move_to)

if __name__ == "__main__":
    main()