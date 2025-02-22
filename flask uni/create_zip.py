import zipfile
import os

def create_zip(file_list, output_path="decrypted_files.zip"):
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for file in file_list:
            zipf.write(file, os.path.basename(file))
    return output_path