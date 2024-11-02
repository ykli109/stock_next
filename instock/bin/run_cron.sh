#!/bin/sh

export PYTHONIOENCODING=utf-8
export LANG=zh_CN.UTF-8
export PYTHONPATH=/data/InStock
export LC_CTYPE=zh_CN.UTF-8

instock_path=$(dirname "$(realpath "$0")")/..

# 环境变量输出
# https://stackoverflow.com/questions/27771781/how-can-i-access-docker-set-environment-variables-from-a-cron-job
printenv | grep -v "no_proxy" >> /etc/environment

# 设置cron任务
chmod 755 $instock_path/bin/run_*.sh
chmod 755 $instock_path/cron/cron.hourly/* $instock_path/cron/cron.workdayly/* $instock_path/cron/cron.monthly/*

# 创建一个临时文件
CRON_FILE=$(mktemp)

# 写入cron任务
cat > $CRON_FILE << EOF
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
# min hour day month weekday command
*/30 9,10,11,13,14,15 * * 1-5 /bin/run-parts instock_path/cron/cron.hourly
30 17 * * 1-5 /bin/run-parts instock_path/cron/cron.workdayly
30 10 * * 3,6 /bin/run-parts instock_path/cron/cron.monthly
EOF

# 安装cron任务
crontab $CRON_FILE

# 删除临时文件
rm $CRON_FILE