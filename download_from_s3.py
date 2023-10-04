import requests
import os
import shutil
import dotenv
import logging

logging.basicConfig(filename='/home/pi/piink/piink.log', level=logging.INFO)

dotenv.load_dotenv()

HOST_URL = os.getenv("HOST_URL")
IMG_URL = os.getenv("IMG_URL")
XML_URL = os.getenv("XML_URL")
OUT_FOLDER = os.getenv("OUT_FOLDER")

if not all([HOST_URL, IMG_URL, XML_URL, OUT_FOLDER]):
    logging.error("Environment variables not set correctly.")
    exit(1)

def download_file(url, local_filename):
    if not url or not local_filename:
        logging.error(f"Invalid parameters. URL: {url}, Local Filename: {local_filename}")
        return

    try:
        with requests.get(url, stream=True) as r:
            if r.status_code != 200:
                logging.error(f"Failed to download. HTTP Status Code: {r.status_code}")
                return

            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded {local_filename}")
    except Exception as e:
        logging.error(f"Error in downloading file: {e}")

if __name__ == "__main__":
    files_to_download = {
        IMG_URL: "/home/pi/piink/media/out.jpg",
        XML_URL: "/home/pi/piink/media/dv_signage.xml",
    }

    try:
        for url, local_path in files_to_download.items():
            download_file(url, local_path)
        shutil.move("/home/pi/piink/media/out.jpg", f"{OUT_FOLDER}/out.jpg")
        shutil.move("/home/pi/piink/media/dv_signage.xml", f"{OUT_FOLDER}/dv_signage.xml")
    except Exception as e:
        logging.error(f"Error in moving files: {e}")
