#!/bin/sh

instock_path=$(dirname "$(realpath "$0")")/..
ps -ef | grep python3 | grep "$instock_path/instock/web/web_service.py" | awk '{print$2}' | xargs kill -9
