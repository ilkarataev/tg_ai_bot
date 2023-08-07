import re,os.path,shutil,time,yadisk
import traceback
import string,random,re
import random,io
from libs import config as configs
from libs import mysql as mysqlfunc
from libs import yandex_libs as yalib
from libs import additional_func as adf
from datetime import datetime

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# A simple list to store some data
data_list = []

@app.route('/')
def hello():
    return 'Hello, this is a simple Python backend!'
@app.route('/rest/v1/get_task_to_render', methods=['GET'])
def get_task_to_render():
    response=mysqlfunc.get_task_to_render()

    return str(response['tg_user_id'])


@app.route('/rest/v1/get_photo_to_render', methods=['POST'])
def get_photo_to_render():
    tg_user_id=''
    if request.method == 'POST':
        # Get the data from the request body
        data = request.json
        tg_user_id = data['tg_user_id']
        if (tg_user_id != ''):
            response_image=mysqlfunc.get_photo_to_render(tg_user_id)
            blob_file = io.BytesIO(response_image)
            # attachment_filename='request.blob'
            #  return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, attachment_filename='data.blob')
            return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name=str(tg_user_id)+'_photo')
        
@app.route('/rest/v1/set_status', methods=['POST'])
def set_status():
    tg_user_id=''
    if request.method == 'POST':
        # Get the data from the request body
        data = request.json
        print(data)
        tg_user_id = data['tg_user_id']
        status = data['status']
        if (tg_user_id != '' and status !=''):
            response=mysqlfunc.set_status(status,tg_user_id)
            return response

@app.route('/rest/v1/', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return jsonify(data_list)
    elif request.method == 'POST':
        # Get the data from the request body
        data = request.json
        # Append the data to the data_list
        data_list.append(data)
        return jsonify({'message': 'Data added successfully'})

if __name__ == '__main__':
    app.run(debug=True)