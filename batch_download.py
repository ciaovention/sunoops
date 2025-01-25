"""
Batch Downloader for Suno.ai URLs

Usage:
    python suno_batch_downloader.py <input-folder>

Description:
    This script processes all URL files named as url.txt, url(1).txt, url(2).txt, etc., 
    within the specified input folder. It downloads each file listed in these URL files 
    and organizes them into 'mp3' and 'mp4' subfolders. If files with the same name 
    already exist, it appends _1, _2, etc., before the file extension to ensure unique filenames.

Example:
    python suno_batch_downloader.py /path/to/url_files_folder
"""

import requests
import os
import sys
import glob

def download_file(url, filepath):
    """Download a file from a URL to a specified filepath."""
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        file.write(chunk)
    except Exception as e:
        raise e

def ensure_directory(path):
    """Ensure that a directory exists; if not, create it."""
    if not os.path.exists(path):
        os.makedirs(path)

def get_unique_filename(directory, filename, existing_names):
    """
    Generate a unique filename within the specified directory.
    If filename exists, append _1, _2, etc., before the extension.
    """
    base, ext = os.path.splitext(filename)
    unique_name = filename
    counter = 1
    while unique_name in existing_names or os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    existing_names.add(unique_name)
    return unique_name

def process_url_file(filepath, mp3_dir, mp4_dir, existing_names):
    """Process a single URL file and download the listed files."""
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            print(f"Skipping invalid line: {line}")
            continue
        filename, url = line.split('|', 1)
        filename = filename.strip()
        url = url.strip()

        if not filename or not url:
            print(f"Skipping incomplete entry: {line}")
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext == '.mp3':
            target_dir = mp3_dir
        elif ext == '.mp4':
            target_dir = mp4_dir
        else:
            print(f"Unsupported file extension for {filename}. Skipping.")
            continue

        try:
            unique_filename = get_unique_filename(target_dir, filename, existing_names)
            target_path = os.path.join(target_dir, unique_filename)
            print(f"Downloading: {unique_filename} from {url}")
            download_file(url, target_path)
            print(f"Successfully downloaded: {unique_filename}")
        except Exception as e:
            print(f"Failed to download {filename} from {url}. Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python suno_batch_downloader.py <input-folder>")
        sys.exit(1)

    input_folder = sys.argv[1]

    if not os.path.isdir(input_folder):
        print(f"Error: The specified input folder does not exist or is not a directory: {input_folder}")
        sys.exit(1)

    # Define output directories
    mp3_dir = os.path.join(input_folder, 'mp3')
    mp4_dir = os.path.join(input_folder, 'mp4')

    # Ensure output directories exist
    ensure_directory(mp3_dir)
    ensure_directory(mp4_dir)

    # Find all url*.txt files in the input folder
    url_files_pattern = os.path.join(input_folder, 'url*.txt')
    url_files = glob.glob(url_files_pattern)

    if not url_files:
        print(f"No URL files found in the input folder: {input_folder}")
        sys.exit(1)

    print(f"Found {len(url_files)} URL file(s) to process.")

    # Keep track of existing filenames to handle duplicates across all files
    existing_names = set()

    # Process each URL file sequentially
    for url_file in sorted(url_files):
        print(f"\nProcessing file: {os.path.basename(url_file)}")
        process_url_file(url_file, mp3_dir, mp4_dir, existing_names)

    print("\nAll downloads completed.")

if __name__ == "__main__":
    main()