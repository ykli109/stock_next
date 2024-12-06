# -*- coding:utf-8 -*-
# !/usr/bin/env python

import pandas as pd
import requests
import instock.core.tablestructure as tbs


__date__ = '2023/5/9 '


def stock_selection() -> pd.DataFrame:
    """
    东方财富网-个股-选股器
    https://data.eastmoney.com/xuangu/
    :return: 选股器
    :rtype: pandas.DataFrame
    """
    cols = tbs.TABLE_CN_STOCK_SELECTION['columns']
    sty = ""  # 初始值 "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,CHANGE_RATE"
    for k in cols:
        sty = f"{sty},{cols[k]['map']}"
    url = "https://data.eastmoney.com/dataapi/xuangu/list"
    current_page = 1
    exception_count = 0
    all_data = []
    while True:
        params = {
            "sty": sty[1:],
            # "上交所主板","深交所主板","深交所创业板","上交所科创板","上交所风险警示板","深交所风险警示板","北京证券交易所","上交所主板","上交所风险警示板","上交所科创板"
            "filter": "(MARKET+in+(\"上交所主板\",\"深交所主板\",\"深交所创业板\"))(NEW_PRICE>0)",
            "p": current_page,
            "ps": 600,
            "source": "SELECT_SECURITIES",
            "client": "WEB"
        }

        try:
            r = requests.get(url, params=params)
            data_json = r.json()
            data = data_json["result"]["data"]
            if not data:
                break
            print(f"当前页码: {current_page}, 数据长度: {len(data)}")
            all_data.extend(data)

            # 检查是否有下一页
            has_next = data_json["result"]["nextpage"]
            if not has_next:
                break
            current_page += 1
        except requests.RequestException as e:
            print(f"HTTP请求失败: {e}")
            exception_count += 1
            if exception_count > 20:
                break
            continue
        except ValueError as e:
            print(f"解析JSON失败: {e}")
            exception_count += 1
            if exception_count > 20:
                break
            continue

    if not all_data:
        return pd.DataFrame()
    temp_df = pd.DataFrame(all_data)

    mask = ~temp_df['CONCEPT'].isna()
    temp_df.loc[mask, 'CONCEPT'] = temp_df.loc[mask, 'CONCEPT'].apply(lambda x: ', '.join(x))
    mask = ~temp_df['STYLE'].isna()
    temp_df.loc[mask, 'STYLE'] = temp_df.loc[mask, 'STYLE'].apply(lambda x: ', '.join(x))

    for k in cols:
        t = tbs.get_field_type_name(cols[k]["type"])
        if t == 'numeric':
            temp_df[cols[k]["map"]] = pd.to_numeric(temp_df[cols[k]["map"]], errors="coerce")
        elif t == 'datetime':
            temp_df[cols[k]["map"]] = pd.to_datetime(temp_df[cols[k]["map"]], errors="coerce").dt.date

    return temp_df


def stock_selection_params():
    """
    东方财富网-个股-选股器-选股指标
    https://data.eastmoney.com/xuangu/
    :return: 选股器-选股指标
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter-web.eastmoney.com/wstock/selection/api/data/get"
    params = {
        "type": "RPTA_PCNEW_WHOLE",
        "sty": "ALL",
        "p": 1,
        "ps": 50000,
        "source": "SELECT_SECURITIES",
        "client": "WEB"
    }

    r = requests.get(url, params=params)
    data_json = r.json()
    zxzb = data_json["zxzb"]  # 指标
    print(zxzb)


if __name__ == "__main__":
    stock_selection_df = stock_selection()
    print(stock_selection)
