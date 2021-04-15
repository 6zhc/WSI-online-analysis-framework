import zipfile
import os


def make_archive_threadsafe(zip_name: str, path: str):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(path):
            for file in files:
                zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
