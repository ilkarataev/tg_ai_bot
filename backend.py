import io
from libs import config as configs
from libs import mysql as mysqlfunc
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

data_list = []

@app.route('/rest/v1/get_task_to_render', methods=['GET'])
def get_task_to_render():
    response=mysqlfunc.get_task_to_render()
    if(response):
        print(response)
        return response
    else:
        return "false"
    
@app.route('/rest/v1/set_rendering_duration', methods=['POST'])
def set_rendering_duration():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        render_time = data['render_time']

        response = mysqlfunc.update_render_time(tg_user_id, render_time)
        return response

@app.route('/rest/v1/update_render_host', methods=['POST'])
def update_render_host_route():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        render_host = data['render_host']

        response = mysqlfunc.update_render_host(tg_user_id, render_host)
        return response


@app.route('/rest/v1/get_photo_to_render', methods=['POST'])
def get_photo_to_render():
    tg_user_id=''
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        if (tg_user_id != ''):
            response_image=mysqlfunc.get_photo_to_render(tg_user_id)
            blob_file = io.BytesIO(response_image)
            return send_file(blob_file, mimetype='application/octet-stream', as_attachment=True, download_name=str(tg_user_id)+'_photo')
        
@app.route('/rest/v1/set_render_host_status', methods=['POST'])
def set_render_host_status():
    tg_user_id=''
    if request.method == 'POST':
        data = request.json
        print(data)
        host_name = data['host_name']
        status = data['status']
        if (tg_user_id != '' and status !=''):
            response=mysqlfunc.set_status(status,host_name)
            return response

@app.route('/rest/v1/set_status', methods=['POST'])
def set_status():
    if request.method == 'POST':
        data = request.json
        tg_user_id = data['tg_user_id']
        status = data['status']
        if (tg_user_id != '' and status !=''):
            response=mysqlfunc.set_status(tg_user_id,status)
            return response

@app.route('/rest/v1/get_bot_token', methods=['POST'])
def data():
    if request.method == 'POST':
        # Get the data from the request body
        data = request.json
        # Append the data to the data_list
        if data['salt'] == 'asdasdsas123213saa':
            return jsonify({'bot_token': configs.bot_token})

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)