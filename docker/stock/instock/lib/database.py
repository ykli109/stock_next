#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量中读取数据库配置
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')
db_port = int(os.getenv('DB_PORT', 3306))  # 提供默认值并转换为整数
db_charset = os.getenv('DB_CHARSET', 'utf8mb4')  # 提供默认值

MYSQL_CONN_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (
    db_user, db_password, db_host, db_port, db_database, db_charset)
logging.info(f"数据库链接信息：{ MYSQL_CONN_URL}")

MYSQL_CONN_DBAPI = {'host': db_host, 'user': db_user, 'password': db_password, 'database': db_database,
                    'charset': db_charset, 'port': db_port, 'autocommit': True}

MYSQL_CONN_TORNDB = {'host': f'{db_host}:{str(db_port)}', 'user': db_user, 'password': db_password,
                     'database': db_database, 'charset': db_charset, 'max_idle_time': 3600, 'connect_timeout': 1000}


# 通过数据库链接 engine
def engine():
    return create_engine(MYSQL_CONN_URL)


def engine_to_db(to_db):
    _engine = create_engine(MYSQL_CONN_URL.replace(f'/{db_database}?', f'/{to_db}?'))
    return _engine


# DB Api -数据库连接对象connection
def get_connection():
    try:
        return pymysql.connect(**MYSQL_CONN_DBAPI)
    except Exception as e:
        logging.error(f"database.conn_not_cursor处理异常：{MYSQL_CONN_DBAPI}{e}")
    return None


# 定义通用方法函数，插入数据库表，并创建数据库主键，保证重跑数据的时候索引唯一。
def insert_db_from_df(data, table_name, cols_type, write_index, primary_keys, indexs=None):
    # 插入默认的数据库。
    insert_other_db_from_df(None, data, table_name, cols_type, write_index, primary_keys, indexs)


# 增加一个插入到其他数据库的方法。
def insert_other_db_from_df(to_db, data, table_name, cols_type, write_index, primary_keys, indexs=None):
    # 定义engine
    logging.info(f"database.insert_other_db_from_df 处理数据：{data}")

    logging.info(f"database.insert_other_db_from_df处理开始：{to_db}{table_name}{cols_type}{write_index}{primary_keys}{indexs}")
    if to_db is None:
        logging.info(f"database.insert_other_db_from_df to_db 为空：{to_db}{table_name}{cols_type}{write_index}{primary_keys}{indexs}")
        engine_mysql = engine()
    else:
        logging.info(f"database.insert_other_db_from_df to_db 不为空：{to_db}{table_name}{cols_type}{write_index}{primary_keys}{indexs}")
        engine_mysql = engine_to_db(to_db)
    # 使用 http://docs.sqlalchemy.org/en/latest/core/reflection.html
    # 使用检查检查数据库表是否有主键。
    ipt = inspect(engine_mysql)
    logging.info(f"database.insert_other_db_from_df inspect：{ipt}")
    col_name_list = data.columns.tolist()
    # 如果有索引，把索引增加到varchar上面。
    if write_index:
        # 插入到第一个位置：
        logging.info(f"database.insert_other_db_from_df write_index：{write_index}")
        col_name_list.insert(0, data.index.name)
    try:
        if cols_type is None:
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db, if_exists='append',
                        index=write_index, )
        elif not cols_type:
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db, if_exists='append',
                        dtype={col_name: NVARCHAR(255) for col_name in col_name_list}, index=write_index, )
        else:
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db, if_exists='append',
                        dtype=cols_type, index=write_index, )
    except Exception as e:
        logging.error(f"database.insert_other_db_from_df处理异常：{table_name}表{e}")

    # 判断是否存在主键
    if not ipt.get_pk_constraint(table_name)['constrained_columns']:
        logging.info(f"database.insert_other_db_from_df 没有主键：{table_name}{cols_type}{write_index}{primary_keys}{indexs}")
        try:
            # 执行数据库插入数据。
            with get_connection() as conn:
                with conn.cursor() as db:
                    db.execute(f'ALTER TABLE `{table_name}` ADD PRIMARY KEY ({primary_keys});')
                    if indexs is not None:
                        for k in indexs:
                            db.execute(f'ALTER TABLE `{table_name}` ADD INDEX IN{k}({indexs[k]});')
        except Exception as e:
            logging.error(f"database.insert_other_db_from_df处理异常：{table_name}表{e}")


# 更新数据
def update_db_from_df(data, table_name, where):
    data = data.where(data.notnull(), None)
    update_string = f'UPDATE `{table_name}` set '
    where_string = ' where '
    cols = tuple(data.columns)
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                for row in data.values:
                    sql = update_string
                    sql_where = where_string
                    for index, col in enumerate(cols):
                        if col in where:
                            if len(sql_where) == len(where_string):
                                if type(row[index]) == str:
                                    sql_where = f'''{sql_where}`{col}` = '{row[index]}' '''
                                else:
                                    sql_where = f'''{sql_where}`{col}` = {row[index]} '''
                            else:
                                if type(row[index]) == str:
                                    sql_where = f'''{sql_where} and `{col}` = '{row[index]}' '''
                                else:
                                    sql_where = f'''{sql_where} and `{col}` = {row[index]} '''
                        else:
                            if type(row[index]) == str:
                                if row[index] is None or row[index] != row[index]:
                                    sql = f'''{sql}`{col}` = NULL, '''
                                else:
                                    sql = f'''{sql}`{col}` = '{row[index]}', '''
                            else:
                                if row[index] is None or row[index] != row[index]:
                                    sql = f'''{sql}`{col}` = NULL, '''
                                else:
                                    sql = f'''{sql}`{col}` = {row[index]}, '''
                    sql = f'{sql[:-2]}{sql_where}'
                    db.execute(sql)
            except Exception as e:
                logging.error(f"database.update_db_from_df处理异常：{sql}{e}")


# 检查表是否存在
def checkTableIsExist(tableName):
    with get_connection() as conn:
        with conn.cursor() as db:
            db.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = '{0}'
                """.format(tableName.replace('\'', '\'\'')))
            if db.fetchone()[0] == 1:
                return True
    return False


# 增删改数据
def executeSql(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
            except Exception as e:
                logging.error(f"database.executeSql处理异常：{sql}{e}")


# 查询数据
def executeSqlFetch(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
                return db.fetchall()
            except Exception as e:
                logging.error(f"database.executeSqlFetch处理异常：{sql}{e}")
    return None


# 计算数量
def executeSqlCount(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
                result = db.fetchall()
                if len(result) == 1:
                    return int(result[0][0])
                else:
                    return 0
            except Exception as e:
                logging.error(f"database.select_count计算数量处理异常：{e}")
    return 0
