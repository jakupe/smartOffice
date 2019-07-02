# smartOffice

**Required programms on raspbian stretch lite**

1. Connect to WiFi/LAN
2. Activate SSH, SPI and Remote GPIO
3. Run: 
```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git python-pip -y
sudo pip install RPi.GPIO spidev 
sudo pip install firebase_admin
cd /home/pi/
git clone https://github.com/lthiery/SPI-Py.git
git clone https://github.com/jakupe/smartOffice.git
cd SPI-Py
git checkout 8cce26b9ee6e69eb041e9d5665944b88688fca68
sudo python setup.py install
cd ..
sudo rm -rf SPI-Py
chmod 755 /home/pi/smartOffice/ScanRFID.py
sed -i -e 's/\r$//' /home/pi/smartOffice/ScanRFID.py
(crontab -l ; echo "@reboot python /home/pi/smartOffice/ScanRFID.py")| crontab -
sudo reboot
```