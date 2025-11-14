#!/bin/bash

echo "=== 日志查看工具 ==="
echo "1. 查看前端运行日志"
echo "2. 查看前端构建日志"
echo "3. 查看前端部署日志"
echo "4. 查看后端运行日志"
echo "5. 查看后端部署日志"
echo "6. 查看所有进程状态"
echo "7. 退出"
echo "=================="

read -p "请选择要查看的日志类型 (1-7): " choice

case $choice in
    1)
        echo "=== 前端运行日志 ==="
        if [ -f "/home/007101/Asset/logs/web.log" ]; then
            tail -f /home/007101/Asset/logs/web.log
        else
            echo "日志文件不存在，请先部署前端服务"
        fi
        ;;
    2)
        echo "=== 前端构建日志 ==="
        if [ -f "/home/007101/Asset/logs/web_build.log" ]; then
            cat /home/007101/Asset/logs/web_build.log
        else
            echo "日志文件不存在，请先部署前端服务"
        fi
        ;;
    3)
        echo "=== 前端部署日志 ==="
        if [ -f "/home/007101/Asset/logs/web_deploy.log" ]; then
            cat /home/007101/Asset/logs/web_deploy.log
        else
            echo "日志文件不存在，请先部署前端服务"
        fi
        ;;
    4)
        echo "=== 后端运行日志 ==="
        if [ -f "/home/007101/Asset/logs/backend.log" ]; then
            tail -f /home/007101/Asset/logs/backend.log
        else
            echo "日志文件不存在，请先部署后端服务"
        fi
        ;;
    5)
        echo "=== 后端部署日志 ==="
        if [ -f "/home/007101/Asset/logs/backend_deploy.log" ]; then
            cat /home/007101/Asset/logs/backend_deploy.log
        else
            echo "日志文件不存在，请先部署后端服务"
        fi
        ;;
    6)
        echo "=== 进程状态 ==="
        echo "前端进程:"
        if [ -f "/home/007101/Asset/logs/web.pid" ]; then
            WEB_PID=$(cat /home/007101/Asset/logs/web.pid)
            if ps -p $WEB_PID > /dev/null; then
                echo "运行中 (PID: $WEB_PID)"
            else
                echo "未运行"
            fi
        else
            echo "未找到PID文件"
        fi
        
        echo "后端进程:"
        if [ -f "/home/007101/Asset/logs/backend.pid" ]; then
            BACKEND_PID=$(cat /home/007101/Asset/logs/backend.pid)
            if ps -p $BACKEND_PID > /dev/null; then
                echo "运行中 (PID: $BACKEND_PID)"
            else
                echo "未运行"
            fi
        else
            echo "未找到PID文件"
        fi
        ;;
    7)
        echo "退出日志查看工具"
        exit 0
        ;;
    *)
        echo "无效选择，请输入 1-7 之间的数字"
        ;;
esac