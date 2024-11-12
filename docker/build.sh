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

# 输出构建 Docker 镜像的命令
echo " docker build -f Dockerfile -t ${DOCKER_NAME} ."

# 登录阿里云镜像仓库
docker login --username=endless_road109 crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com
# 构建 Docker 镜像，并打上两个标签
docker build -t crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG1}  -t crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG2} .
# 推送 Docker 镜像到阿里云镜像仓库
docker push crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG1}
docker push crpi-92qbf85cobo30phq.cn-shanghai.personal.cr.aliyuncs.com/${DOCKER_NAME}:${TAG2}


# 登录 Docker Hub
docker login --username=ykli109 
# 构建 Docker 镜像，使用 Dockerfile，并打上两个标签
docker build -f Dockerfile -t ${DOCKER_NAME}:${TAG1} -t ${DOCKER_NAME}:${TAG2} .
# 输出推送 Docker 镜像的命令
echo " docker push ${DOCKER_NAME} "

# 推送带有 TAG1 的 Docker 镜像到 Docker 仓库
docker push ${DOCKER_NAME}:${TAG1}

# 推送带有 TAG2 的 Docker 镜像到 Docker 仓库
docker push ${DOCKER_NAME}:${TAG2}