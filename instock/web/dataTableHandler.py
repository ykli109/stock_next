#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from abc import ABC
from tornado import gen
import datetime
import instock.lib.trade_time as trd
import instock.core.singleton_stock_web_module_data as sswmd
import instock.web.base as webBase
import time
from typing import Optional, Dict, Any


__date__ = '2023/3/10 '


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return "是" if ord(obj) == 1 else "否"
        elif isinstance(obj, datetime.date):
            delta = datetime.datetime.combine(obj, datetime.time.min) - datetime.datetime(1899, 12, 30)
            return f'/OADate({float(delta.days) + (float(delta.seconds) / 86400)})/'  # 86,400 seconds in day
            # return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


# 获得页面数据。
class GetStockHtmlHandler(webBase.BaseHandler, ABC):
    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        web_module_data = sswmd.stock_web_module_data().get_data(name)
        run_date, run_date_nph = trd.get_trade_date_last()
        if web_module_data.is_realtime:
            date_now_str = run_date_nph.strftime("%Y-%m-%d")
        else:
            date_now_str = run_date.strftime("%Y-%m-%d")
        self.render("stock_web.html", web_module_data=web_module_data, date_now=date_now_str,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 获得股票数据内容。
class GetStockDataHandler(webBase.BaseHandler, ABC):
    # 缓存数据结构：{cache_key: (timestamp, data)}
    _cache: Dict[str, tuple[float, list[Any]]] = {}
    CACHE_EXPIRE_TIME = 600  # 缓存有效期10分钟（单位：秒）
    
    @staticmethod
    def _get_cache_key(name: str, date: Optional[str]) -> str:
        """生成缓存键"""
        return f"{name}:{date if date else 'all'}"
    
    def _get_cached_data(self, cache_key: str) -> Optional[list[Any]]:
        """获取缓存数据，如果缓存无效或过期返回None"""
        if cache_key not in self._cache:
            return None
            
        timestamp, data = self._cache[cache_key]
        
        # 检查缓存是否过期
        if time.time() - timestamp > self.CACHE_EXPIRE_TIME:
            del self._cache[cache_key]
            return None
            
        # 如果数据为空，视为无效缓存
        if not data:
            del self._cache[cache_key]
            return None
            
        return data
    
    def _set_cache(self, cache_key: str, data: list[Any]) -> None:
        """设置缓存数据"""
        # 只缓存非空数据
        if data:
            self._cache[cache_key] = (time.time(), data)
            
            # 如果缓存项超过100个，删除最旧的缓存
            if len(self._cache) > 100:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
    
    def get(self):
        name = self.get_argument("name", default=None, strip=False)
        date = self.get_argument("date", default=None, strip=False)
        
        # 尝试从缓存获取数据
        cache_key = self._get_cache_key(name, date)
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            self.set_header('Content-Type', 'application/json;charset=UTF-8')
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.set_header('Access-Control-Allow-Headers', 'Content-Type')
            self.write(json.dumps(cached_data, cls=MyEncoder))
            print(f"缓存命中: {cache_key}")
            return
            
        # 缓存未命中，从数据库查询
        print(f"缓存未命中: {cache_key}")
        web_module_data = sswmd.stock_web_module_data().get_data(name)
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')

        if date is None:
            where = ""
        else:
            where = f" WHERE `date` = '{date}'"

        order_by = ""
        if web_module_data.order_by is not None:
            order_by = f" ORDER BY {web_module_data.order_by}"

        order_columns = ""
        if web_module_data.order_columns is not None:
            order_columns = f",{web_module_data.order_columns}"

        sql = f" SELECT *{order_columns} FROM `{web_module_data.table_name}`{where}{order_by}"

        data = self.db.query(sql)
        
        # 设置缓存
        self._set_cache(cache_key, data)
        
        self.write(json.dumps(data, cls=MyEncoder))
