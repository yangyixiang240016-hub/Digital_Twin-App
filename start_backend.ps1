# 污水处理厂后端服务启动脚本
Write-Host "启动污水处理厂后端服务..." -ForegroundColor Green
Write-Host ""

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python未找到"
    }
    Write-Host "Python已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Python，请先安装Python" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "安装时请勾选 'Add Python to PATH'" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 进入backend目录
Set-Location backend

# 检查是否存在虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 安装依赖
Write-Host "安装Python依赖包..." -ForegroundColor Yellow
pip install -r requirements.txt

# 启动服务
Write-Host ""
Write-Host "启动后端服务..." -ForegroundColor Green
Write-Host "服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""
python run_server.py

Read-Host "按回车键退出"
