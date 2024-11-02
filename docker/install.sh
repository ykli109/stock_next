#!/bin/bash
# 设置语言环境
export LANG=zh_CN.UTF-8
export LC_CTYPE=zh_CN.UTF-8
export LC_ALL=C

# 替换apt源为阿里云
sed -i "s@http://\(deb\|security\).debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list

# 设置pip源为阿里云
mkdir -p /etc/pip
cat > /etc/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple
trusted-host = mirrors.aliyun.com
EOF

# 设置时区
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo "Asia/Shanghai" > /etc/timezone

# 安装依赖
apt-get update
apt-get install -y cron gcc make python3-dev default-libmysqlclient-dev build-essential pkg-config curl

# 安装Python包
pip install -r /path/to/requirements.txt
pip install supervisor mysqlclient requests arrow numpy==1.26.4 SQLAlchemy PyMySQL \
    Logbook python_dateutil py_mini_racer tqdm beautifulsoup4 bokeh pandas tornado easytrader

# 安装TA-Lib
curl -SL https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz | tar -xzC .
cd ta-lib/
./configure --prefix=/usr
make && make install
cd ..
pip install TA-Lib
rm -rf ta-lib*

# 清理
apt-get --purge remove -y gcc make python3-dev default-libmysqlclient-dev curl
rm -rf /root/.cache/* /var/lib/apt/lists/*
apt-get clean && apt-get autoclean && apt-get autoremove -y 