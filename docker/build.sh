#!/bin/sh

# 删除当前目录下的 stock 目录
rm -rf stock

# 使用 rsync 从上级目录复制 stock 目录到当前目录，排除指定的文件和目录
rsync -av --progress ../../stock . \
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
DOCKER_NAME=ykli/instock

# 获取当前日期并格式化为 YYYYMM，用于版本标签
TAG1=$(date "+%Y%m")

# 定义最新版本标签
TAG2=latest

# 输出构建 Docker 镜像的命令
echo " docker build -f Dockerfile -t ${DOCKER_NAME} ."

# # 构建 Docker 镜像，使用 Dockerfile，并打上两个标签
docker build -f Dockerfile -t ${DOCKER_NAME}:${TAG1} -t ${DOCKER_NAME}:${TAG2} .

# 输出分隔线
echo "#################################################################"

# 输出推送 Docker 镜像的命令
echo " docker push ${DOCKER_NAME} "

# 推送带有 TAG1 的 Docker 镜像到 Docker 仓库
docker push ${DOCKER_NAME}:${TAG1}

# 推送带有 TAG2 的 Docker 镜像到 Docker 仓库
docker push ${DOCKER_NAME}:${TAG2}