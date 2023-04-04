#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from typing import Any


class BaseJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, Result):
            return o.__dict__
        return super().default(o)


class Result(object):

    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    def __init__(self, data: object, status: str = STATUS_SUCCESS, message: str = "") -> None:
        self.data = data
        self.status = status
        self.message = message

    def default(self, o):
        return super().default(o)

    def __repr__(self) -> str:
        return json.dumps(self, ensure_ascii=False, cls=BaseJsonEncoder)

    def __str__(self) -> str:
        return repr(self)

    @staticmethod
    def success(data: object, message: str = "操作成功") -> object:
        return Result(data, status=Result.STATUS_SUCCESS, message=message)

    @staticmethod
    def failed(data: object, message: str = "操作失败") -> object:
        return Result(data=data, status=Result.STATUS_FAILED, message=message)


if __name__ == "__main__":
    result1 = Result([1, 2, 3], Result.STATUS_SUCCESS, "test")
    result2 = Result.success([4, 5, 6])
    result3 = Result.failed([7, 8, 9])
    print(result1)
    print(result2)
    print(result3)
