@echo off
echo 启动污水处理厂后端服务...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo Python已安装，版本信息:
python --version
echo.

REM 进入backend目录
cd backend

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装Python依赖包...
pip install -r requirements.txt

REM 启动服务
echo.
echo 启动后端服务...
echo 服务地址: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.
python run_server.py

pause
