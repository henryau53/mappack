#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from typing import Any, Dict, List
from core.constants import EPSG3857, EPSG4326
from core.utils import map
from core.tianditu import packer

# 全局下载任务记录缓存，用于记录某个下载进度与情况
download_progress_cache = {}
# 下载状态常量
DOWNLOAD_STATE_DOWNLOADING = "ing"
DOWNLOAD_STATE_COMPLETE = "ed"
DOWNLOAD_STATE_CANCEL = "un"


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

    download_progress_cache[uuid] = {}
    # 记录当前下载唯一标识
    download_progress_cache[uuid]["uuid"] = uuid
    # 记录当前下载状态
    download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_DOWNLOADING
    # 记录当前下载类型
    download_progress_cache[uuid]["type"] = map_type
    # 记录当前下载投影类型
    download_progress_cache[uuid]["projection"] = EPSG4326
    # 记录当前下载层级
    download_progress_cache[uuid]["zoom"] = zoom
    # 记录瓦片位置信息
    download_progress_cache[uuid]["tile"] = {
        "nw": tile_nw,
        "se": tile_se,
    }
    # 记录当前下载信息
    download_progress_cache[uuid]["current"] = {
        "total": 0,
        "row": 0,
        "col": 0,
    }
    # 记录需要下载共计多少
    download_progress_cache[uuid]["total"] = total
    # 记录下载失败的详情列表
    download_progress_cache[uuid]["failed"] = []

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            download_progress_cache[uuid]["current"]["row"] = row
            download_progress_cache[uuid]["current"]["col"] = col
            # 如果取消了下载，则停止循环下载
            if download_progress_cache[uuid]["state"] == DOWNLOAD_STATE_CANCEL:
                result = False
                type_str = "影像地图" if map_type == "img" else "矢量地图"
                logging.info(f"\033[1;31m取消{zoom}级{type_str}的EPSG4326下载，当前进度{row}行，{col}列\033[0m")
                break

            success = packer.download_tile(zoom, row, col, map_type, EPSG4326)
            download_progress_cache[uuid]["current"]["total"] += 1
            if not success:
                result = False
                download_progress_cache[uuid]["failed"].append({
                    "zoom": zoom,
                    "row": row,
                    "col": col,
                })
        else:  # 仅在内循环不中断时执行
            continue
        break

    if download_progress_cache[uuid]["state"] != DOWNLOAD_STATE_CANCEL:
        download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_COMPLETE

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

    download_progress_cache[uuid] = {}
    # 记录当前下载唯一标识
    download_progress_cache[uuid]["uuid"] = uuid
    # 记录当前下载状态
    download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_DOWNLOADING
    # 记录当前下载类型
    download_progress_cache[uuid]["type"] = map_type
    # 记录当前下载投影类型
    download_progress_cache[uuid]["projection"] = EPSG3857
    # 记录当前下载层级
    download_progress_cache[uuid]["zoom"] = zoom
    # 记录瓦片位置信息
    download_progress_cache[uuid]["tile"] = {
        "nw": tile_nw,
        "se": tile_se,
    }
    # 记录当前下载信息
    download_progress_cache[uuid]["current"] = {
        "total": 0,
        "row": 0,
        "col": 0,
    }
    # 记录需要下载共计多少
    download_progress_cache[uuid]["total"] = total
    # 记录下载失败的详情列表
    download_progress_cache[uuid]["failed"] = []

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            download_progress_cache[uuid]["current"]["row"] = row
            download_progress_cache[uuid]["current"]["col"] = col
            # 如果取消了下载，则停止循环下载
            if download_progress_cache[uuid]["state"] == DOWNLOAD_STATE_CANCEL:
                result = False
                type_str = "影像地图" if map_type == "img" else "矢量地图"
                logging.info(f"\033[1;31m取消{zoom}级{type_str}的EPSG3857下载，当前进度{row}行，{col}列\033[0m")
                break

            success = packer.download_tile(zoom, row, col, map_type, EPSG3857)
            download_progress_cache[uuid]["current"]["total"] += 1
            if not success:
                result = False
                download_progress_cache[uuid]["failed"].append({
                    "zoom": zoom,
                    "row": row,
                    "col": col,
                })
        else:  # 仅在内循环不中断时执行
            continue
        break

    if download_progress_cache[uuid]["state"] != DOWNLOAD_STATE_CANCEL:
        download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_COMPLETE

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


def resume_progress(uuid: str) -> bool:
    """恢复指定唯一标识的下载

    Args:
        uuid (str): 唯一标识

    Returns:
        bool: 全部下载成功返回True，如果有下载失败的瓦片或者缓存进度不存在了则返回False
    """
    if uuid not in download_progress_cache:
        return False

    # 防抖
    if download_progress_cache[uuid]["state"] == DOWNLOAD_STATE_DOWNLOADING:
        return False

    download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_DOWNLOADING

    tile_nw = download_progress_cache[uuid]["tile"]["nw"]
    tile_se = download_progress_cache[uuid]["tile"]["se"]

    _, start_col, _ = tile_nw
    end_row, end_col, _ = tile_se
    resume_row = download_progress_cache[uuid]["current"]["row"]
    resume_col = download_progress_cache[uuid]["current"]["col"]

    if download_progress_cache[uuid]["current"]["total"] == download_progress_cache[uuid][
            "total"] and end_row == resume_row and end_col == resume_col:
        download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_COMPLETE
        return True

    result = True
    zoom = download_progress_cache[uuid]["zoom"]
    epsg_code = download_progress_cache[uuid]["projection"]
    map_type = download_progress_cache[uuid]["type"]

    col = resume_col
    for row in range(resume_row, end_row + 1):
        while col < end_col + 1:
            download_progress_cache[uuid]["current"]["row"] = row
            download_progress_cache[uuid]["current"]["col"] = col
            # 如果取消了下载，则停止循环下载
            if download_progress_cache[uuid]["state"] == DOWNLOAD_STATE_CANCEL:
                result = False
                type_str = "影像地图" if map_type == "img" else "矢量地图"
                epsg_str = "EPSG4326" if epsg_code == EPSG4326 else "EPSG3857"
                logging.info(f"\033[1;31m取消{zoom}级{type_str}的{epsg_str}下载，当前进度{row}行，{col}列\033[0m")
                break

            success = packer.download_tile(zoom, row, col, map_type, epsg_code)
            download_progress_cache[uuid]["current"]["total"] += 1
            if not success:
                result = False
                download_progress_cache[uuid]["failed"].append({
                    "zoom": zoom,
                    "row": row,
                    "col": col,
                })
            col += 1
        else:  # 仅在内循环不中断时执行
            col = start_col
            continue
        break

    if download_progress_cache[uuid]["state"] != DOWNLOAD_STATE_CANCEL:
        download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_COMPLETE

        if epsg_code == EPSG4326:
            # 计算坐标区域的瓦片四个原点坐标
            coordinate_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
            coordinate_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
        # elif epsg_code in [EPSG3857, EPSG900913]:
        else:
            # 计算瓦片原点坐标
            origin3857_nw = map.tianditu_tile_position_to_EPSG3857(*tile_nw)
            origin3857_se = map.tianditu_tile_position_to_EPSG3857(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])

            # 米坐标（EPSG3857）转换经纬度坐标
            coordinate_nw = map.EPSG3857_to_EPSG4326(*origin3857_nw)
            coordinate_se = map.EPSG3857_to_EPSG4326(*origin3857_se)

        # 合成瓦片大图
        packer.bundle_tiles(zoom, map_type, epsg_code)
        # 转换瓦片格式
        packer.translate_bundle(zoom, coordinate_nw, coordinate_se, map_type, epsg_code)

    return result


def cancel_progress(uuid: str) -> None:
    """设置下载缓存中指定唯一标识的状态，即取消下载

    Args:
        uuid (str): 唯一标识
    """
    if uuid in download_progress_cache:
        download_progress_cache[uuid]["state"] = DOWNLOAD_STATE_CANCEL


def get_progress(uuid: str) -> Dict[str, Any]:
    """根据唯一标识获取下载记录信息

    Args:
        uuid (str): 唯一标识

    Returns:
        Dict[str, Any]: 记录信息
    """
    return download_progress_cache[uuid] if uuid in download_progress_cache else None


def delete_progress(uuid: str) -> bool:
    """根据唯一标识删除下载记录信息

    Args:
        uuid (str): 唯一标识

    Returns:
        bool: 是否成功
    """
    if uuid in download_progress_cache:
        del download_progress_cache[uuid]
        return True
    return False
