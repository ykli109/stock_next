#!/bin/sh

instock_path=$(dirname "$(realpath "$0")")/..

python3 $instock_path/job/execute_daily_job.py

