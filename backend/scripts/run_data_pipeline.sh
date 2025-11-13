#!/bin/bash

# 数据管道脚本：先执行新增数据操作，再执行更新使用人操作
# 使用方法: ./run_data_pipeline.sh <更新文件路径>

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# 创建日志目录
LOG_DIR="$BACKEND_DIR/logs"
mkdir -p "$LOG_DIR"

# 获取当前时间戳
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 <更新文件路径>"
    echo "示例: $0 /path/to/update_file.xlsx"
    exit 1
fi

UPDATE_FILE="$1"
if [ ! -f "$UPDATE_FILE" ]; then
    echo "错误：更新文件 '$UPDATE_FILE' 不存在"
    exit 1
fi

# 步骤1：执行新增数据操作
echo "=== 步骤1：执行新增数据操作 ==="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 执行新增数据操作
cd "$BACKEND_DIR"
if python "$SCRIPT_DIR/add_new_data.py" "$UPDATE_FILE" 2>&1 | tee "$LOG_DIR/add_new_data_${TIMESTAMP}.log"; then
    echo "新增数据操作执行成功"
else
    echo "错误：新增数据操作执行失败"
    exit 1
fi

# 步骤2：执行更新使用人操作
echo "=== 步骤2：执行更新使用人操作 ==="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 执行更新使用人操作
if python "$SCRIPT_DIR/update_user_data.py" "$UPDATE_FILE" 2>&1 | tee "$LOG_DIR/update_user_data_${TIMESTAMP}.log"; then
    echo "更新使用人操作执行成功"
else
    echo "错误：更新使用人操作执行失败"
    exit 1
fi

echo "=== 数据管道执行完成 ==="
echo "日志文件保存在: $LOG_DIR/"
echo "add_new_data_${TIMESTAMP}.log - 新增数据操作日志"
echo "update_user_data_${TIMESTAMP}.log - 更新使用人操作日志"