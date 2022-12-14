from .connection import DBContextManager
from typing import List


def select(dbconfig: dict, _sql: str):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')

        cursor.execute(_sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result, schema


def edit(dbconfig: dict, _sql: str):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')

        cursor.execute(_sql)


def select_dict(db_config: dict, sql: str) -> List:
    result = []
    with DBContextManager(db_config) as cursor:

        if cursor is None:
            raise ValueError('Курсор не создан')

        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]

        for row in cursor.fetchall():
            result.append(dict(zip(schema, row)))

    return result


def insert(dbconfig: dict, _sql: str):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        cursor.execute(_sql)
        return cursor.connection.insert_id()


def call_proc(dbconfig: dict, proc_name: str, *args):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не курсор')
        param_list = []
        for arg in args:
            print('args=', arg)
            param_list.append(arg)
        print('param_list', param_list)
        res = cursor.callproc(proc_name, param_list)
    return res