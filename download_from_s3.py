import requests
import os
import shutil
import dotenv
import logging
import datetime
import json

logging.basicConfig(filename='/home/pi/piink/piink.log', level=logging.INFO)

dotenv.load_dotenv()

HOST_URL = os.getenv("HOST_URL")
IMG_URL = os.getenv("IMG_URL")
XML_URL = os.getenv("XML_URL")
OUT_FOLDER = os.getenv("OUT_FOLDER")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_slack_notification(message):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'text': message
    }
    response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
    return response

if not all([HOST_URL, IMG_URL, XML_URL, OUT_FOLDER]):
    logging.error("Environment variables not set correctly.")
    exit(1)

def replace_img_in_xml(xml_path, img_name):
    if not xml_path or not img_name:
        logging.error(f"Invalid parameters. XML Path: {xml_path}, Image Path: {img_name}")
        return

    try:
        with open(xml_path, 'r') as f:
            xml = f.read()
            xml = xml.replace("out", str(img_name))
        with open(xml_path, 'w') as f:
            f.write(xml)
        logging.info(f"Replaced image path in {xml_path}")
    except Exception as e:
        logging.error(f"Error in replacing image path: {e}")
        send_slack_notification(f"PiInk - Error in replacing image path: {e}")

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
        send_slack_notification(f"PiInk - Error in downloading file: {e}")

if __name__ == "__main__":
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    files_to_download = {
        IMG_URL: "/home/pi/piink/media/out.jpg",
        XML_URL: "/home/pi/piink/media/dv_signage.xml",
    }
    try:
        for url, local_path in files_to_download.items():
            download_file(url, local_path)
        replace_img_in_xml("/home/pi/piink/media/dv_signage.xml", filename)
        shutil.move("/home/pi/piink/media/out.jpg", f"{OUT_FOLDER}/{filename}.jpg")
        shutil.move("/home/pi/piink/media/dv_signage.xml", f"{OUT_FOLDER}/dv_signage.xml")
        send_slack_notification(f"PiInk - Successfully moved files to {OUT_FOLDER}")
    except Exception as e:
        logging.error(f"Error in moving files: {e}")
        send_slack_notification(f"PiInk - Error in moving files: {e}")
