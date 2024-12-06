#!/bin/bash

set -ex

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 日志文件路径
LOG_FILE="${SCRIPT_DIR}/cron_job.log"

# 激活 Python 虚拟环境
source "${SCRIPT_DIR}/venv/bin/activate"

# 记录开始时间
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始执行任务" >> "$LOG_FILE"

# 执行run_job.sh并记录输出到日志文件
"${SCRIPT_DIR}/instock/bin/run_job.sh" >> "$LOG_FILE" 2>&1

# 记录结束时间和执行状态
if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 任务执行成功" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 任务执行失败" >> "$LOG_FILE"
fi

# 退出虚拟环境
deactivate
