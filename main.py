#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Tuple
from flask import Flask
from flask import render_template
from flask import request
from core.beans import Result
import flask_configs
import core.utils.map as map
import core.tianditu.packer as packer

app = Flask(__name__)
app.config.from_object(flask_configs)

# 全局下载任务记录缓存，用于记录某个下载进度与情况
download_task_cache = {}


@app.route("/")
def hello() -> str:
    """根目录请求

    Returns:
        str: 模板渲染结果
    """
    return render_template("tianditu.html")


@app.route("/info/rectangle", methods=["POST"])
def get_rectangle_info() -> Tuple[str, int]:
    """根据POST参数计算矩形区域的瓦片坐标与瓦片顶点坐标

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    data = request.get_json()
    level = int(data["zoom"])

    # 计算瓦片坐标
    tile_nw = map.tianditu_EPSG4326_to_tile_position(*data["nw"], level)
    tile_ne = map.tianditu_EPSG4326_to_tile_position(*data["ne"], level)
    tile_se = map.tianditu_EPSG4326_to_tile_position(*data["se"], level)
    tile_sw = map.tianditu_EPSG4326_to_tile_position(*data["sw"], level)

    # 计算坐标区域的瓦片四个原点坐标
    coordinate_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
    coordinate_ne = map.tianditu_tile_position_to_EPSG4326(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    coordinate_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    coordinate_sw = map.tianditu_tile_position_to_EPSG4326(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    # 响应返回数据
    result = {
        "coordinate": {
            "nw": coordinate_nw,
            "ne": coordinate_ne,
            "se": coordinate_se,
            "sw": coordinate_sw,
        },
        "tile": {
            "nw": tile_nw,
            "ne": tile_ne,
            "se": tile_se,
            "sw": tile_sw,
        },
        "zoom": level,
    }

    return str(Result.success(result)), 200


@app.route("/download/progress/<uuid>", methods=["GET", "DELETE"])
def download_progress(uuid: str) -> Tuple[str, int]:
    """根据请求方式，删除或者获取指定uuid的下载进度缓存。

    Args:
        uuid (str): 下载任务唯一标识码

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    if request.method == "DELETE":
        if uuid in download_task_cache:
            # 清除下载进度缓存
            del download_task_cache[uuid]
            return str(Result.success(None)), 200
        return str(Result.failed(None)), 200
    else:
        result = download_task_cache[uuid] if uuid in download_task_cache else None
        return str(Result.success(result)), 200


@app.route("/download/tiles", methods=["POST"])
def tiles_download() -> Tuple[str, int]:
    """根据POST传参下载指定范围与层级的瓦片图。

    Returns:
        Tuple[str, int]: Flask 返回值
    """
    data = request.get_json()
    uuid = data["uuid"]
    level = int(data["zoom"])

    # 计算瓦片坐标
    tile_nw = map.tianditu_EPSG4326_to_tile_position(*data["nw"], level)
    tile_ne = map.tianditu_EPSG4326_to_tile_position(*data["ne"], level)
    tile_se = map.tianditu_EPSG4326_to_tile_position(*data["se"], level)
    tile_sw = map.tianditu_EPSG4326_to_tile_position(*data["sw"], level)
    start_row, start_col, _ = tile_nw
    end_row, end_col, _ = tile_se

    total = abs(end_row - start_row + 1) * abs(end_col - start_col + 1)

    download_task_cache[uuid] = {}
    # 记录当前下载层级
    download_task_cache[uuid]["level"] = level
    # 记录当前已经下载多少
    download_task_cache[uuid]["current"] = 0
    # 记录需要下载共计多少
    download_task_cache[uuid]["total"] = total
    # 记录下载失败的详情列表
    download_task_cache[uuid]["failed"] = []

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            success = packer.download_tile(level, row, col)
            download_task_cache[uuid]["current"] += 1
            if not success:
                download_task_cache[uuid]["failed"].append({
                    "level": level,
                    "row": row,
                    "col": col,
                })

    # 计算坐标区域的瓦片四个原点坐标
    coordinate_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
    coordinate_ne = map.tianditu_tile_position_to_EPSG4326(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    coordinate_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    coordinate_sw = map.tianditu_tile_position_to_EPSG4326(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    # 合成瓦片大图
    packer.bundle_tiles(level)
    # 转换瓦片格式
    packer.translate_bundle(level, coordinate_nw, coordinate_se)

    # 响应返回数据
    result = {
        "coordinate": {
            "nw": coordinate_nw,
            "ne": coordinate_ne,
            "se": coordinate_se,
            "sw": coordinate_sw,
        },
        "tile": {
            "nw": tile_nw,
            "ne": tile_ne,
            "se": tile_se,
            "sw": tile_sw,
        },
        "zoom": level,
    }

    return str(Result.success(result)), 200


if __name__ == "__main__":
    app.run()
