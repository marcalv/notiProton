# notiProton
This is a small Python Selenium project scraps protonmail inbox and notifies unread mails via Telegram.

This python script is running on a Raspberry Pi 3 on buster.

## Dependencies
```
sudo apt install git chromium-browser chromium-chromedriver xvfb python3 python3-pip
pip3 install pipenv 
```
## Installation
Clone from repo, install dependencies with pipenv, create config.py and customize it.
```
cd /home/pi
git clone https://github.com/marcalv/notiProton
cd notiProton
pipenv install
pipenv run pip install cffi
pipenv run pip install cryptography
cp config_template.py config.py
nano config.py
```
## Single run
```
pipenv run python -u /home/pi/notiProton/notiProton.py 
```
## Cron Jobs
Example cron jobs:
```
# Every 15 minutes updates and logs std & err to fb.log, wich is monthly deleted.
*/15 0-1,7-23 * * * PATH_TO_VIRUALENV/bin/python -u /home/pi/notiProton/notiProton.py >> /home/pi/notiProton/log.log 2>&1 &
00 3 1,15 * * rm /home/pi/notiProton/log.log
```
Replace `PATH_TO_VIRUALENV` with virtualenv path. You can find it with the following command:
```
pipenv --venv
```
