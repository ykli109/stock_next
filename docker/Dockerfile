# 使用 Python 3.13 的精简版基础镜像
FROM docker.io/python:3.13-slim-bullseye

# 维护者信息
MAINTAINER ykli109
# 设置语言环境为中文
ENV LANG=zh_CN.UTF-8 
# 设置字符类型为中文
ENV LC_CTYPE=zh_CN.UTF-8
# 设置所有区域设置为 C
ENV LC_ALL=C
# 设置 Python模块搜索路径
ENV PYTHONPATH=/data/InStock
# 暴露 9988 端口
EXPOSE 9988

# 设置工作目录为
WORKDIR /data

# 复制应用文件
COPY stock /data/InStock

# 复制install.sh到/tmp/install.sh并执行
COPY install.sh /tmp/install.sh
RUN chmod +x /tmp/install.sh && /tmp/install.sh && \
    rm -f /tmp/install.sh

RUN chmod +x /data/InStock/instock/bin/*.sh
# 设置容器启动时执行的命令
ENTRYPOINT ["supervisord","-n","-c","/data/InStock/supervisor/supervisord.conf"]