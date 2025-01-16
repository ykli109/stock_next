#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2022/5/16 15:31
Desc: 东方财富网-数据中心-大宗交易-市场统计
http://data.eastmoney.com/dzjy/dzjy_sctj.aspx
"""
import pandas as pd
import requests

def stock_dzjy_mrtj(start_date: str = '20220105', end_date: str = '20220105') -> pd.DataFrame:
    """
    东方财富网-数据中心-大宗交易-每日统计
    http://data.eastmoney.com/dzjy/dzjy_mrtj.aspx
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :return: 每日统计
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        'sortColumns': 'TURNOVERRATE',
        'sortTypes': '-1',
        'pageSize': '5000',
        'pageNumber': '1',
        'reportName': 'RPT_BLOCKTRADE_STA',
        'columns': 'TRADE_DATE,SECURITY_CODE,SECUCODE,SECURITY_NAME_ABBR,CHANGE_RATE,CLOSE_PRICE,AVERAGE_PRICE,PREMIUM_RATIO,DEAL_NUM,VOLUME,DEAL_AMT,TURNOVERRATE,D1_CLOSE_ADJCHRATE,D5_CLOSE_ADJCHRATE,D10_CLOSE_ADJCHRATE,D20_CLOSE_ADJCHRATE',
        'source': 'WEB',
        'client': 'WEB',
        'filter': f"(TRADE_DATE>='{'-'.join([start_date[:4], start_date[4:6], start_date[6:]])}')(TRADE_DATE<='{'-'.join([end_date[:4], end_date[4:6], end_date[6:]])}')"
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json['result']["data"])
    temp_df.reset_index(inplace=True)
    temp_df['index'] = temp_df.index + 1
    temp_df.columns = [
        "序号",
        "交易日期",
        "证券代码",
        "-",
        "证券简称",
        "涨跌幅",
        "收盘价",
        "成交价",
        "折溢率",
        "成交笔数",
        "成交总量",
        "成交总额",
        "成交总额/流通市值",
        "_",
        "_",
        "_",
        "_",
    ]
    temp_df["交易日期"] = pd.to_datetime(temp_df["交易日期"]).dt.date
    temp_df = temp_df[[
        "序号",
        "交易日期",
        "证券代码",
        "证券简称",
        "收盘价",
        "涨跌幅",
        "成交价",
        "折溢率",
        "成交笔数",
        "成交总量",
        "成交总额",
        "成交总额/流通市值",
    ]]
    temp_df['涨跌幅'] = pd.to_numeric(temp_df['涨跌幅'])
    temp_df['收盘价'] = pd.to_numeric(temp_df['收盘价'])
    temp_df['成交价'] = pd.to_numeric(temp_df['成交价'])
    temp_df['折溢率'] = pd.to_numeric(temp_df['折溢率'])
    temp_df['成交笔数'] = pd.to_numeric(temp_df['成交笔数'])
    temp_df['成交总量'] = pd.to_numeric(temp_df['成交总量'])
    temp_df['成交总额'] = pd.to_numeric(temp_df['成交总额'])
    temp_df['成交总额/流通市值'] = pd.to_numeric(temp_df['成交总额/流通市值'])
    return temp_df


if __name__ == "__main__":
    stock_dzjy_mrtj_df = stock_dzjy_mrtj(start_date='20201204', end_date='20201204')
    print(stock_dzjy_mrtj_df)
