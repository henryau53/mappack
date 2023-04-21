#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from typing import Tuple
from flask import Flask
from flask import render_template, send_from_directory
from flask import request
from core.beans import Result
from core.constants import EPSG4326, EPSG3857, EPSG900913
from core.handlers import tianditu as tianditu_handler
import flask_configs

app = Flask(__name__)
app.config.from_object(flask_configs)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/image'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def hello() -> str:
    """根目录请求

    Returns:
        str: 模板渲染结果
    """
    return "<h2>Hello, Mappack !!!</h2>"


@app.route("/tianditu/<projection>", methods=["GET"])
def tianditu(projection: str) -> str:
    """根据请求参数路由对应的天地图投影页面，包括EPSG4326经纬度与EPSG3857墨卡托

    Args:
        projection (str): 投影坐标系代号，4326或3857（900913），其它值默认跳转4326

    Returns:
        str: 模板渲染结果
    """
    value = EPSG3857 if projection in ("3857", "900913") else EPSG4326
    return render_template("tianditu.html", projection=value)


@app.route("/tianditu/info/rectangle", methods=["POST"])
def get_rectangle_info() -> Tuple[str, int]:
    """根据POST参数计算矩形区域的瓦片坐标与瓦片原点坐标

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    data = request.get_json()
    projection = str(data["projection"])
    result = None

    if projection == EPSG4326:
        result = tianditu_handler.rectangle_of_EPSG4326(data["nw"], data["ne"], data["se"], data["sw"], int(data["zoom"]))
    elif projection in (EPSG3857, EPSG900913):
        result = tianditu_handler.rectangle_of_EPSG3857(data["nw"], data["ne"], data["se"], data["sw"], int(data["zoom"]))

    return str(Result.success(result)), 200


@app.route("/tianditu/download/tiles", methods=["POST"])
def tiles_download() -> Tuple[str, int]:
    """根据POST传参下载指定范围与层级的瓦片图。

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    data = request.get_json()
    uuid = str(data["uuid"])
    projection = str(data["projection"])
    map_type = str(data["type"])
    zoom = int(data["zoom"])
    result = False
    if projection == EPSG4326:
        result = tianditu_handler.download_tiles_of_EPSG4326(uuid, data["nw"], data["ne"], data["se"], data["sw"], zoom,
                                                             map_type)
    elif projection in (EPSG3857, EPSG900913):
        result = tianditu_handler.download_tiles_of_EPSG3857(uuid, data["nw"], data["ne"], data["se"], data["sw"], zoom,
                                                             map_type)
    return str(Result.success(result)), 200


@app.route("/tianditu/download/cancel", methods=["POST"])
def cancel_tiles_download() -> Tuple[str, int]:
    """根据POST传参下载指定范围与层级的瓦片图。

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    data = request.get_json()
    uuid = str(data["uuid"])
    tianditu_handler.cancel_progress(uuid)
    return str(Result.success(True)), 200


@app.route("/tianditu/download/progress/<uuid>", methods=["GET", "DELETE"])
def download_progress(uuid: str) -> Tuple[str, int]:
    """根据请求方式，删除或者获取指定uuid的下载进度缓存。

    Args:
        uuid (str): 下载任务唯一标识码

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    if request.method == "DELETE":
        result = tianditu_handler.delete_progress(uuid)
        if result:
            return str(Result.success(result)), 200
        else:
            return str(Result.failed(result)), 200
    else:
        result = tianditu_handler.get_progress(uuid)
        return str(Result.success(result)), 200


if __name__ == "__main__":
    app.run()
