import requests
import os
import shutil
import dotenv

dotenv.load_dotenv()

# Define your public S3 bucket URLs here
HOST_URL = os.getenv("HOST_URL")
IMG_URL = os.getenv("IMG_URL")
XML_URL = os.getenv("XML_URL")
OUT_FOLDER = os.getenv("OUT_FOLDER")

def download_file(url, local_filename):
    """Download file from a given URL.

    Parameters:
        url (str): URL to download from
        local_filename (str): Local path where the file will be saved
    """
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {local_filename}")

if __name__ == "__main__":
    # Define your public S3 bucket URLs here
    files_to_download = {
        "IMG_URL": "/home/pi/piink/media/out.jpg",
        "XML_URL": "/home/pi/piink/media/dv_signage.xml",
    }

    for url, local_path in files_to_download.items():
        download_file(url, local_path)
        
    shutil.move("/home/pi/piink/media/out.jpg", f"{OUT_FOLDER}/out.jpg")
    shutil.move("/home/pi/piink/media/dv_signage.xml", f"{OUT_FOLDER}/dv_signage.xml")
