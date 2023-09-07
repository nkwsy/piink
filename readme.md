chmod +x download_from_s3.py

sudo cp download_from_s3.service /etc/systemd/system/

#sudo nano /etc/systemd/system/download_from_s3.service

sudo systemctl enable download_from_s3.service
sudo systemctl start download_from_s3.service



####

2880 x 2160
