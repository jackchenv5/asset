#!/bin/bash

# 创建日志目录
mkdir -p /home/007101/Asset/logs

# 进入前端目录
cd /home/007101/Asset/web

# 构建项目
echo "开始构建前端项目..." >> /home/007101/Asset/logs/web_deploy.log
pnpm build >> /home/007101/Asset/logs/web_build.log 2>&1

if [ $? -eq 0 ]; then
    echo "前端项目构建成功" >> /home/007101/Asset/logs/web_deploy.log
else
    echo "前端项目构建失败" >> /home/007101/Asset/logs/web_deploy.log
    exit 1
fi

# 停止之前的进程（如果存在）
if [ -f "/home/007101/Asset/logs/web.pid" ]; then
    OLD_PID=$(cat /home/007101/Asset/logs/web.pid)
    if ps -p $OLD_PID > /dev/null; then
        echo "停止之前的前端进程: $OLD_PID" >> /home/007101/Asset/logs/web_deploy.log
        kill $OLD_PID
    fi
fi

# 启动前端服务
echo "启动前端服务..." >> /home/007101/Asset/logs/web_deploy.log
nohup pnpm run preview --host 0.0.0.0 --port 3000 > /home/007101/Asset/logs/web.log 2>&1 &
WEB_PID=$!
echo $WEB_PID > /home/007101/Asset/logs/web.pid

echo "前端服务启动成功，PID: $WEB_PID，日志文件: /home/007101/Asset/logs/web.log" >> /home/007101/Asset/logs/web_deploy.log
echo "前端部署完成！"
