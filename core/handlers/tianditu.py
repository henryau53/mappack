#!/usr/bin/env python
# -*- coding:utf-8 -*-

from typing import Any, Dict, List
from core.constants import EPSG3857, EPSG4326
from core.utils import map
from core.tianditu import packer

# 全局下载任务记录缓存，用于记录某个下载进度与情况
download_task_cache = {}


def rectangle_of_EPSG4326(nw: List[float], ne: List[float], se: List[float], sw: List[float], zoom: int) -> Dict[str, Any]:
    """获取EPSG4326投影下的矩形选区信息

    Args:
        nw (List[float]): 左上角经纬度坐标
        ne (List[float]): 右上角经纬度坐标
        se (List[float]): 右下角经纬度坐标
        sw (List[float]): 左下角经纬度坐标
        zoom (int): 层级

    Returns:
        Dict[str, Any]: 选区信息
    """

    # 计算瓦片坐标
    tile_nw = map.tianditu_EPSG4326_to_tile_position(*nw, zoom)
    tile_ne = map.tianditu_EPSG4326_to_tile_position(*ne, zoom)
    tile_se = map.tianditu_EPSG4326_to_tile_position(*se, zoom)
    tile_sw = map.tianditu_EPSG4326_to_tile_position(*sw, zoom)

    # 计算坐标区域的瓦片四个原点坐标
    origin4326_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
    origin4326_ne = map.tianditu_tile_position_to_EPSG4326(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    origin4326_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    origin4326_sw = map.tianditu_tile_position_to_EPSG4326(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    return {
        "zoom": zoom,
        "coordinate": {
            "nw": origin4326_nw,
            "ne": origin4326_ne,
            "se": origin4326_se,
            "sw": origin4326_sw,
        },
        "tile": {
            "nw": tile_nw,
            "ne": tile_ne,
            "se": tile_se,
            "sw": tile_sw,
        },
    }


def rectangle_of_EPSG3857(nw: List[float], ne: List[float], se: List[float], sw: List[float], zoom: int) -> Dict[str, Any]:
    """获取EPSG3857投影下的矩形选区信息

    Args:
        nw (List[float]): 左上角经纬度坐标
        ne (List[float]): 右上角经纬度坐标
        se (List[float]): 右下角经纬度坐标
        sw (List[float]): 左下角经纬度坐标
        zoom (int): 层级

    Returns:
        Dict[str, Any]: 选区信息
    """

    # 经纬度坐标转换米坐标（EPSG3857）
    coordinate3857_nw = map.EPSG4326_to_EPSG3857(*nw)
    coordinate3857_ne = map.EPSG4326_to_EPSG3857(*ne)
    coordinate3857_se = map.EPSG4326_to_EPSG3857(*se)
    coordinate3857_sw = map.EPSG4326_to_EPSG3857(*sw)

    # 计算瓦片行列坐标
    tile_nw = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_nw, zoom)
    tile_ne = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_ne, zoom)
    tile_se = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_se, zoom)
    tile_sw = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_sw, zoom)

    # 计算瓦片原点坐标
    origin3857_nw = map.tianditu_tile_position_to_EPSG3857(*tile_nw)
    origin3857_ne = map.tianditu_tile_position_to_EPSG3857(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    origin3857_se = map.tianditu_tile_position_to_EPSG3857(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    origin3857_sw = map.tianditu_tile_position_to_EPSG3857(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    # 米坐标（EPSG3857）转换经纬度坐标
    origin4326_nw = map.EPSG3857_to_EPSG4326(*origin3857_nw)
    origin4326_ne = map.EPSG3857_to_EPSG4326(*origin3857_ne)
    origin4326_se = map.EPSG3857_to_EPSG4326(*origin3857_se)
    origin4326_sw = map.EPSG3857_to_EPSG4326(*origin3857_sw)

    return {
        "zoom": zoom,
        "coordinate": {
            "nw": origin4326_nw,
            "ne": origin4326_ne,
            "se": origin4326_se,
            "sw": origin4326_sw,
        },
        "tile": {
            "nw": tile_nw,
            "ne": tile_ne,
            "se": tile_se,
            "sw": tile_sw,
        },
    }


def download_tiles_of_EPSG4326(uuid: str, nw: List[float], ne: List[float], se: List[float], sw: List[float], zoom: int,
                               map_type: str) -> bool:
    """下载EPSG4326投影下的瓦片

    Args:
        uuid (str): 唯一标识
        nw (List[float]): 左上角经纬度坐标
        ne (List[float]): 右上角经纬度坐标
        se (List[float]): 右下角经纬度坐标
        sw (List[float]): 左下角经纬度坐标
        zoom (int): 层级
        map_type (str): 地图类型，img|vec

    Returns:
        bool: 全部下载成功返回True，如果有下载失败的瓦片，则返回False
    """
    result = True
    # 计算瓦片坐标
    tile_nw = map.tianditu_EPSG4326_to_tile_position(*nw, zoom)
    # tile_ne = map.tianditu_EPSG4326_to_tile_position(*ne, zoom)
    tile_se = map.tianditu_EPSG4326_to_tile_position(*se, zoom)
    # tile_sw = map.tianditu_EPSG4326_to_tile_position(*sw, zoom)

    start_row, start_col, _ = tile_nw
    end_row, end_col, _ = tile_se

    total = abs(end_row - start_row + 1) * abs(end_col - start_col + 1)

    download_task_cache[uuid] = {}
    # 记录当前下载类型
    download_task_cache[uuid]["type"] = map_type
    # 记录当前下载层级
    download_task_cache[uuid]["zoom"] = zoom
    # 记录当前已经下载多少
    download_task_cache[uuid]["current"] = 0
    # 记录需要下载共计多少
    download_task_cache[uuid]["total"] = total
    # 记录下载失败的详情列表
    download_task_cache[uuid]["failed"] = []

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            success = packer.download_tile(zoom, row, col, map_type, EPSG4326)
            download_task_cache[uuid]["current"] += 1
            if not success:
                result = False
                download_task_cache[uuid]["failed"].append({
                    "zoom": zoom,
                    "row": row,
                    "col": col,
                })

    # 计算坐标区域的瓦片四个原点坐标
    coordinate_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
    # coordinate_ne = map.tianditu_tile_position_to_EPSG4326(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    coordinate_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    # coordinate_sw = map.tianditu_tile_position_to_EPSG4326(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    # 合成瓦片大图
    packer.bundle_tiles(zoom, map_type, EPSG4326)
    # 转换瓦片格式
    packer.translate_bundle(zoom, coordinate_nw, coordinate_se, map_type, EPSG4326)

    return result


def download_tiles_of_EPSG3857(uuid: str, nw: List[float], ne: List[float], se: List[float], sw: List[float], zoom: int,
                               map_type: str) -> bool:
    """下载EPSG3857投影下的瓦片

    Args:
        uuid (str): 唯一标识
        nw (List[float]): 左上角经纬度坐标
        ne (List[float]): 右上角经纬度坐标
        se (List[float]): 右下角经纬度坐标
        sw (List[float]): 左下角经纬度坐标
        zoom (int): 层级
        map_type (str): 地图类型，img|vec

    Returns:
        bool: 全部下载成功返回True，如果有下载失败的瓦片，则返回False
    """
    result = True
    # 经纬度坐标转换米坐标（EPSG3857）
    coordinate3857_nw = map.EPSG4326_to_EPSG3857(*nw)
    # coordinate3857_ne = map.EPSG4326_to_EPSG3857(*ne)
    coordinate3857_se = map.EPSG4326_to_EPSG3857(*se)
    # coordinate3857_sw = map.EPSG4326_to_EPSG3857(*sw)

    # 计算瓦片行列坐标
    tile_nw = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_nw, zoom)
    # tile_ne = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_ne, zoom)
    tile_se = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_se, zoom)
    # tile_sw = map.tianditu_EPSG3857_to_tile_position(*coordinate3857_sw, zoom)

    start_row, start_col, _ = tile_nw
    end_row, end_col, _ = tile_se

    total = abs(end_row - start_row + 1) * abs(end_col - start_col + 1)

    download_task_cache[uuid] = {}
    # 记录当前下载类型
    download_task_cache[uuid]["type"] = map_type
    # 记录当前下载层级
    download_task_cache[uuid]["zoom"] = zoom
    # 记录当前已经下载多少
    download_task_cache[uuid]["current"] = 0
    # 记录需要下载共计多少
    download_task_cache[uuid]["total"] = total
    # 记录下载失败的详情列表
    download_task_cache[uuid]["failed"] = []

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            success = packer.download_tile(zoom, row, col, map_type, EPSG3857)
            download_task_cache[uuid]["current"] += 1
            if not success:
                result = False
                download_task_cache[uuid]["failed"].append({
                    "zoom": zoom,
                    "row": row,
                    "col": col,
                })

    # 计算瓦片原点坐标
    origin3857_nw = map.tianditu_tile_position_to_EPSG3857(*tile_nw)
    # origin3857_ne = map.tianditu_tile_position_to_EPSG3857(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    origin3857_se = map.tianditu_tile_position_to_EPSG3857(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    # origin3857_sw = map.tianditu_tile_position_to_EPSG3857(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    # 米坐标（EPSG3857）转换经纬度坐标
    origin4326_nw = map.EPSG3857_to_EPSG4326(*origin3857_nw)
    # origin4326_ne = map.EPSG3857_to_EPSG4326(*origin3857_ne)
    origin4326_se = map.EPSG3857_to_EPSG4326(*origin3857_se)
    # origin4326_sw = map.EPSG3857_to_EPSG4326(*origin3857_sw)

    # 合成瓦片大图
    packer.bundle_tiles(zoom, map_type, EPSG3857)
    # 转换瓦片格式
    packer.translate_bundle(zoom, origin4326_nw, origin4326_se, map_type, EPSG3857)

    return result


def get_progress(uuid: str) -> Dict[str, Any]:
    """根据唯一标识获取下载记录信息

    Args:
        uuid (str): 唯一标识

    Returns:
        Dict[str, Any]: 记录信息
    """
    return download_task_cache[uuid] if uuid in download_task_cache else None


def delete_progress(uuid: str) -> bool:
    """根据唯一标识删除下载记录信息

    Args:
        uuid (str): 唯一标识

    Returns:
        bool: 是否成功
    """
    if uuid in download_task_cache:
        del download_task_cache[uuid]
        return True
    return False
