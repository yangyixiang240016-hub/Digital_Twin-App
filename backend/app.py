import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from flask_cors import CORS
from routes import register_routes

app = Flask(__name__)

# 配置CORS，允许所有跨域请求
CORS(app, 
     origins='*', 
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

register_routes(app)  # 注册所有模块的路由

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
