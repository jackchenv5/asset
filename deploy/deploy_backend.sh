#!/bin/bash

# 创建日志目录
mkdir -p /home/007101/Asset/logs

# 进入后端目录
cd /home/007101/Asset/backend

# 激活虚拟环境
source venv/bin/activate

# 停止之前的进程（如果存在）
if [ -f "/home/007101/Asset/logs/backend.pid" ]; then
    OLD_PID=$(cat /home/007101/Asset/logs/backend.pid)
    if ps -p $OLD_PID > /dev/null; then
        echo "停止之前的后端进程: $OLD_PID" >> /home/007101/Asset/logs/backend_deploy.log
        kill $OLD_PID
    fi
fi

# 启动后端服务
echo "启动后端服务..." >> /home/007101/Asset/logs/backend_deploy.log
nohup python manage.py runserver 0.0.0.0:8002 > /home/007101/Asset/logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /home/007101/Asset/logs/backend.pid

echo "后端服务启动成功，PID: $BACKEND_PID，日志文件: /home/007101/Asset/logs/backend.log" >> /home/007101/Asset/logs/backend_deploy.log
echo "后端部署完成！"
