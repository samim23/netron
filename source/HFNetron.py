#!/usr/bin/env python

##########################################
########## HF Netron Model Saver #########
##########################################

####### Imports #######

import os
import json
import pathlib
import threading
import time
import requests

from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

####### Utility #######

def writeToLog(text):
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'static','log.json')
    f = open(filename,'w')
    f.write(text)
    f.close()

####### App Setup #######

# app = Flask(__name__)
currentpath = pathlib.Path(__file__).parent.resolve()
print('currentpath', currentpath)
app = Flask(__name__, static_url_path='/static', static_folder=currentpath)
app.config.from_object(__name__)
app.jinja_env.auto_reload = True

####### App Routes #######

# index
@app.route("/")
def hello():
    return "Hello World!"

####### App API Routes #######

@app.route('/settings_save', methods=['POST'])
def settings_save():
    form = request.form
    form = json.dumps(form, indent=2)
    # data = request.get_json()
    # form = jsonify(data)
    # print('settings_save',form)

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'modelsettings.json')
    f = open(filename,'w+')
    f.write(form)
    f.close()
    return json.dumps({'status':'OK','form':form})

####### Selenium ####### 
# Download driver: https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(str(currentpath) + '/chromedriver')

@app.before_first_request
def activate_job():
    def run_job():
        print("Run Selenium")
        driver.get("http://localhost:8888/static/index.html?url=https://huggingface.co/ScottMueller/Cats_v_Dogs.ONNX/resolve/main/cats_v_dogs.onnx")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'message-button'))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'toolbar'))).click()
        # WebDriverWait(driver, 10)
        print('Netron model loaded: ' + str(driver.title))

    thread = threading.Thread(target=run_job)
    thread.start()

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://localhost:8888/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


####### App Start #######

if __name__ == '__main__':
    print('-------------- HF Netron Saver --------------')
    start_runner()
    app.run(debug=True,port=8888)


