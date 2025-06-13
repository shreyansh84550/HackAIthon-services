import os
from classifyFile import processFile;

def process_files_in_folder(folder_path):
    """
    Reads and processes each file in the specified folder.

    Args:
        folder_path (str): The path to the folder containing the files.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            process_single_file(folder_path, filename)

def process_single_file(folder_path, filename):
    """
    Processes a single file.

    Args:
        folder_path (str): The path to the folder containing the file.
        filename (str): The name of the file to process.
    """
    file_path = os.path.join(folder_path, filename)
    print(f"Processing file: {file_path}")
    processDocumentResult = processFile(file_path)
    print(f"The Result is: " , processDocumentResult)
