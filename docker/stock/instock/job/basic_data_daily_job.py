#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os.path
import sys

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.lib.run_template as runt
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.core.stockfetch as stf
from instock.core.singleton_stock import stock_data

__author__ = 'myh '
__date__ = '2023/3/10 '


# 股票实时行情数据。
def save_nph_stock_spot_data(date, before=True):
    logging.info(f"basic_data_daily_job.save_nph_stock_spot_data处理开始：{date}{before}")
    if before:
        return  # 如果 before 为 True，直接返回，不执行后续操作

    # 股票列表
    try:
        data = stock_data(date).get_data()  # 获取指定日期的股票数据
        if data is None or len(data.index) == 0:
            logging.info(f"basic_data_daily_job.save_nph_stock_spot_data 没有获取到数据：{date}{before}")
            return  # 如果没有获取到数据，直接返回

        logging.info(f"basic_data_daily_job.save_nph_stock_spot_data 获取到数据：{data}")
        table_name = tbs.TABLE_CN_STOCK_SPOT['name']  # 获取表名
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):  # 检查表是否存在
            logging.info(f"basic_data_daily_job.save_nph_stock_spot_data 表已存在：{date}{before}")
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"  # 构建删除语句
            result = mdb.executeSql(del_sql)  # 执行删除操作
            if result is not None:
                logging.info(f"成功删除 {result} 行数据，日期：{date}")
            else:
                logging.warning(f"删除操作未返回任何结果，日期：{date}")
            cols_type = None  # 如果表存在，列类型设为 None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_SPOT['columns'])  # 获取列类型

        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")  # 将数据插入数据库

    except Exception as e:
        logging.error(f"basic_data_daily_job.save_stock_spot_data处理异常：{e}")  # 记录异常信息


# 基金实时行情数据。
def save_nph_etf_spot_data(date, before=True):
    if before:
        return
    # 股票列表
    try:
        data = stf.fetch_etfs(date)
        if data is None or len(data.index) == 0:
            return

        table_name = tbs.TABLE_CN_ETF_SPOT['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_ETF_SPOT['columns'])

        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
    except Exception as e:
        logging.error(f"basic_data_daily_job.save_nph_etf_spot_data处理异常：{e}")


def main():
    runt.run_with_args(save_nph_stock_spot_data)
    runt.run_with_args(save_nph_etf_spot_data)


# main函数入口
if __name__ == '__main__':
    main()
