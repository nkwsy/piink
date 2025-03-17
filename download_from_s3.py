import requests
import os
import shutil
import dotenv
import logging
import datetime
import json
import socket
import time

# Update logging configuration to include timestamp in the format
logging.basicConfig(
    filename='/home/pi/piink/piink.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

dotenv.load_dotenv()

HOST_URL = os.getenv("HOST_URL")
IMG_URL = os.getenv("IMG_URL")
XML_URL = os.getenv("XML_URL")
OUT_FOLDER = os.getenv("OUT_FOLDER")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def check_internet_connection(max_retries=3, retry_delay=5):
    """
    Check if there is an active internet connection by attempting to connect to a reliable host.
    
    Args:
        max_retries: Maximum number of retries before giving up
        retry_delay: Delay in seconds between retries
        
    Returns:
        bool: True if internet connection is available, False otherwise
    """
    host = "8.8.8.8"  # Google's DNS server
    port = 53  # DNS port
    
    for attempt in range(max_retries):
        try:
            # Try to create a socket connection to Google's DNS
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            logging.info("Internet connection is available")
            return True
        except Exception as e:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.warning(f"[{current_time}] Internet connection check failed (attempt {attempt+1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.error(f"[{current_time}] No internet connection available after {max_retries} attempts")
    send_slack_notification(f"PiInk - Error: No internet connection available at {current_time}")
    return False

def send_slack_notification(message):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'text': message
    }
    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        return response
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Failed to send Slack notification: {e}")
        return None

if not all([HOST_URL, IMG_URL, XML_URL, OUT_FOLDER]):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.error(f"[{current_time}] Environment variables not set correctly.")
    exit(1)

def replace_img_in_xml(xml_path, img_name):
    if not xml_path or not img_name:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Invalid parameters. XML Path: {xml_path}, Image Path: {img_name}")
        return

    try:
        with open(xml_path, 'r') as f:
            xml = f.read()
            xml = xml.replace("out", str(img_name))
        with open(xml_path, 'w') as f:
            f.write(xml)
        logging.info(f"Replaced image path in {xml_path}")
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Error in replacing image path: {e}")
        send_slack_notification(f"PiInk - Error in replacing image path: {e} at {current_time}")

def download_file(url, local_filename):
    if not url or not local_filename:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Invalid parameters. URL: {url}, Local Filename: {local_filename}")
        return
    try:
        with requests.get(url, stream=True, timeout=12) as r:
            if r.status_code != 200:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.error(f"[{current_time}] Failed to download. HTTP Status Code: {r.status_code}")
                return
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded {local_filename}")
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Error in downloading file: {e}")
        send_slack_notification(f"PiInk - Error in downloading file: {e} at {current_time}")

if __name__ == "__main__":
    # First check if internet connection is available
    if not check_internet_connection():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Exiting because no internet connection is available.")
        exit(1)
        
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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{current_time}] Error in moving files: {e}")
        send_slack_notification(f"PiInk - Error in moving files: {e} at {current_time}")
