#!/bin/bash

instock_path=$(dirname "$(realpath "$0")")/..
python3 $instock_path/web/web_service.py

echo ------Web服务已启动 请不要关闭------
echo 访问地址 : http://localhost:9988/
