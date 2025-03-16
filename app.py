from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import requests
import os
from datetime import datetime
from queue import Queue
from threading import Lock
import re
import urllib.parse

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

# 请求队列和锁
request_queue = Queue()
queue_lock = Lock()
active_clients = set()

# 确保存储目录存在
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # 检查连接来源
    is_admin = request.args.get('admin') == 'true'
    if not is_admin:
        with queue_lock:
            active_clients.add(request.sid)
            # 向所有客户端广播更新的客户端列表
            socketio.emit('client_list_update', {'clients': list(active_clients)})
            # 通知客户端其ID
            socketio.emit('client_id', {'client_id': request.sid}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    with queue_lock:
        active_clients.discard(request.sid)
        # 向所有客户端广播更新的客户端列表
        socketio.emit('client_list_update', {'clients': list(active_clients)})

@socketio.on('url_fetch_result')
def handle_url_fetch_result(data):
    print(f"Received fetch result from client: {data}")
    # 这里可以处理客户端返回的结果
    if data.get('success'):
        print(f"Successfully fetched URL: {data.get('url')}")
    else:
        print(f"Failed to fetch URL: {data.get('url')} - {data.get('error')}")

@app.route('/request-url-fetch', methods=['POST'])
def request_url_fetch():
    data = request.json
    url = data.get('url')
    client_id = data.get('client_id')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not active_clients:
        return jsonify({'error': 'No active clients available'}), 503
    
    if client_id:
        if client_id not in active_clients:
            return jsonify({'error': 'Selected client is not available'}), 404
        # 向指定客户端发送请求
        socketio.emit('fetch_url_request', {'url': url}, room=client_id)
        message = f'Request sent to client {client_id}'
    else:
        # 向所有连接的客户端发送请求
        socketio.emit('fetch_url_request', {'url': url})
        message = 'Request sent to all clients'
    
    return jsonify({
        'status': 'success',
        'message': message,
        'active_clients': len(active_clients)
    })

@app.route('/fetch-url', methods=['POST'])
def fetch_url():
    # 检查是否有文件上传
    if 'file' in request.files:
        # 从客户端接收文件内容
        file = request.files['file']
        url = request.form.get('url')
        
        if not file:
            return jsonify({'error': 'File content is required'}), 400
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        try:
            # 获取文件名
            filename = file.filename
            filename = urllib.parse.unquote(filename)
            # 确保文件名是合法的
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # 处理文件名重复
            base_name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join('downloads', filename)):
                filename = f'{base_name}({counter}){ext}'
                counter += 1
            
            filepath = os.path.join('downloads', filename)
            
            # 保存文件内容
            file.save(filepath)
            
            return jsonify({
                'status': 'success',
                'message': f'Content saved to {filename}',
                'filename': filepath
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # 兼容旧版本的API，如果没有文件上传，则尝试从JSON中获取URL
    else:
        data = request.json
        url = data.get('url') if data else None
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        try:
            # 使用服务器请求获取URL内容
            response = requests.get(url)
            response.raise_for_status()
            
            # 从响应头或URL中获取文件名
            content_disposition = response.headers.get('content-disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = re.findall('filename=(.+)', content_disposition)[0].strip('"')
            else:
                filename = os.path.basename(url.split('?')[0]) or 'downloaded_file'
                # URL解码文件名
                filename = urllib.parse.unquote(filename)
            
            # 确保文件名是合法的
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # 处理文件名重复
            base_name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join('downloads', filename)):
                filename = f'{base_name}({counter}){ext}'
                counter += 1
            
            filepath = os.path.join('downloads', filename)
            
            # 保存内容
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return jsonify({
                'status': 'success',
                'message': f'Content saved to {filename}',
                'filename': filepath
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)