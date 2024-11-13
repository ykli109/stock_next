#!/bin/sh

# 删除当前目录下的 stock 目录
rm -rf stock

stock_path=$(realpath $(dirname "$(realpath "$0")")/..)

# 使用 rsync 从上级目录复制 stock 目录到当前目录，排除指定的文件和目录
cd $stock_path/docker
rsync -av --progress $stock_path . \
    --exclude .git \
    --exclude .idea \
    --exclude *.md \
    --exclude *.bat \
    --exclude __pycache__ \
    --exclude .gitignore \
    --exclude stock/cron \
    --exclude stock/img \
    --exclude stock/docker \
    --exclude instock/cache \
    --exclude instock/log \
    --exclude instock/test

# 定义 Docker 镜像名称
DOCKER_NAME=ykli109/instock

# 获取当前日期并格式化为 YYYYMM，用于版本标签
TAG1=$(date "+%Y%m%d%H%M")

# 定义最新版本标签
TAG2=latest

# 登录阿里云镜像仓库
echo 'login to aliyun ACR'
docker login --username=endless_road109 crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com

# 登录 Docker Hub
echo 'login to docker hub'
docker login --username=ykli109 

# 构建 Docker 镜像，并打上标签
docker build -t ${DOCKER_NAME}:${TAG1} -t ${DOCKER_NAME}:${TAG2} .

# 标记镜像为阿里云仓库的标签
docker tag ${DOCKER_NAME}:${TAG1} crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG1}
docker tag ${DOCKER_NAME}:${TAG2} crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG2}

# 推送 Docker 镜像到阿里云镜像仓库
docker push crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG1}
docker push crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG2}

# 推送到 Docker Hub
docker push ${DOCKER_NAME}:${TAG1}
docker push ${DOCKER_NAME}:${TAG2}