#!/usr/bin/env python
import time
import sys
import os
import datetime
import atexit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tinydb import TinyDB, Query
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#Exit handler: ensure driver and display are closed
def exit_handler():
    print('Entered in exit handler')
    print('Quitting driver...')
    try:
        driver.quit()
    except:
        print("Couldn't quit driver")
    if not debug:
        print('Stopping display...')
        try:
            display.stop()
        except:
             print("Couldn't stop display")
    print('Bye')
    print("")
    print("")
    sys.exit()

atexit.register(exit_handler)

def create_driver():
    print('Loading driver')
    if debug:
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headlessDebug:
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        display = ''
        print( 'Driver loaded')
    else:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1600, 1200))
        display.start()
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        print('Driver loaded')

    return driver,display

def request_inbox(driver):
    #Start Automations
    print('GET to homepage...')
    driver.get("https://mail.protonmail.com")

    #Wait for "iniciar sesion" button to appear
    WebDriverWait(driver, elementTimeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
    print('Submiting login credentials...')
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(user)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="login_btn"]').click()

    #Wait for Mode Select appear
    print("Wait load conversation list...")
    modeSelect_xpath =  '//*[@id="conversation-list-columns"]'
    WebDriverWait(driver, elementTimeout).until(EC.visibility_of_element_located((By.XPATH, modeSelect_xpath)))

    #Set unread only
    print("GET to unread...")
    driver.get("https://mail.protonmail.com/inbox?filter=unread")


    #Wait for Mode Select appear
    print("Wait load conversation list...")
    modeSelect_xpath =  '//*[@id="conversation-list-columns"]'
    WebDriverWait(driver, elementTimeout).until(EC.visibility_of_element_located((By.XPATH, modeSelect_xpath)))

    inboxText = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/section').text

    print("Inbox acquired")

    return inboxText

def parse_inbox(inboxText):
    print("Parsing inbox...")
    #Parse inbox text
    import re
    inboxText = re.sub('(\([0-9]\))+', '', inboxText).replace('\n ','')
    textLines = inboxText.split('\n')

    #Cleanup parse
    inbox=[]
    for line in textLines:
        if line == "" or line == " ":
            textLines.remove(line)

    #Generate inbox object
    for i in range(0,len(textLines),3):
        mail = {}
        mail["subject"]=textLines[i]
        mail["time"]=textLines[i+1]
        mail["contact"]=textLines[i+2]
        inbox.append(mail)

    return inbox


def mail_exists(mail):
    Search = Query()
    if db.search((Search.subject == mail["subject"]) & (Search.time == mail["time"]) & (Search.contact == mail["contact"]))  == []:
        return False
    else:
        return True

def db_insert(mail):
    Search = Query()
    if not mail_exists(mail):    
        db.insert(mail)

def notify(mail,last):
    if last:
        text="📨 <b>"+mail["subject"]+'</b>\n'+'✏️'+mail["contact"]+'\n'+'🕘'+mail["time"]+'\n\n\n\n\n\n➖'
    else:
        text="📨 <b>"+mail["subject"]+'</b>\n'+'✏️'+mail["contact"]+'\n'+'🕘'+mail["time"]
    bot_send(text)
    return

def bot_send(text):
    bot.send_message(chat_id=chatId,text=text, parse_mode=telegram.ParseMode.HTML)
    return

def manage_inbox(inbox):
    print('Managing Inbox...')
    newMails = []
    for mail in inbox:
        if not mail_exists(mail):
            newMails.append(mail)
    print("============")
    print('New mails: '+str(len(newMails)))
    print("============")

    for index in range(len(newMails)):
        if len(newMails) == index+1:
            notify(newMails[index],True)
        else:
            notify(newMails[index],False)
        db_insert(newMails[index])
    return

#Program Start
print("===================================================")
print(datetime.datetime.now())
print("===================================================")

#Import config variables from config.py
from config import *

#Initialize db and bot
installation_path = os.path.dirname(os.path.realpath(__file__))
db_path = (os.path.join(installation_path, 'db.json'))
db = TinyDB(db_path
)
bot = telegram.Bot(token=botToken)

#Create driver
driver,display=create_driver()

#get inbox with selenium
inboxText=request_inbox(driver)

#parse inbox
inbox=parse_inbox(inboxText)

#Manage inbox
manage_inbox(inbox)

#Exit handler runs here
