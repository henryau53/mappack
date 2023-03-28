#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from typing import Tuple

# 经纬度坐标系WGS84：EPSG:4326，地图单位为度
# 伪墨卡托投影（Pseudo-Mercator）：EPSG:3857，地图单位为米

# 地球半径
R = 6378137
# 地球周长
C = 2 * math.pi * R


def EPSG4326_to_EPSG3857(lng: float, lat: float) -> Tuple[float, float]:
    """经纬度坐标转伪墨卡托坐标

    Args:
        lng (float): 经度
        lat (float): 纬度

    Returns:
        Tuple[float, float]: 伪墨卡托坐标元组
    """

    x = lng * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return (x, y)


def EPSG3857_to_EPSG4326(lng, lat):
    """伪墨卡托坐标转经纬度坐标

    Args:
        lng (float): 经度
        lat (float): 纬度

    Returns:
        Tuple[float, float]: 经纬度坐标元组
    """
    x = lng / 20037508.34 * 180
    y = lat / 20037508.34 * 180
    y = 180 / math.pi * (2 * math.atan(math.exp(y * math.pi / 180)) - math.pi / 2)
    return (x, y)


def get_meters_per_pixel(zoom: int, tile_size=256) -> float:
    """获取指定层级瓦片地图上一像素代表的米数

    Args:
        zoom (int): 层级
        tile_size (int, optional): 瓦片分辨率. 默认值 256.

    Returns:
        float: 米/像素
    """
    # 瓦片金字塔，计算该层级的瓦片长度（个数）（参考 wmts.img_w.xml）
    # 1级共计4个瓦片图，横纵各2张
    # 2级共计16个瓦片图，横纵各4张
    # 3级共计64个瓦片图，横纵各8张，依次类推
    tile_count = math.pow(2, zoom)
    # 计算该层级的像素长度
    total_pixel = tile_size * tile_count
    # 地球周长除以总像素长度，获取每像素多少米
    return C / total_pixel


def tianditu_EPSG3857_to_tile_position(lng: float, lat: float, zoom: int) -> Tuple[int, int, int]:
    """通过伪墨卡托 Pseudo-Mercator（EPSG3857）坐标（该经纬度为墨卡托坐标）获取天地图的瓦片图的行号列号

    Args:
        lng (float): 经度
        lat (float): 纬度
        zoom (_type_): 地图层级

    Returns:
        Tuple[int, int, int]: 元组（行号，列号，层级），该计算方式瓦片图索引从0开始
    """
    # 在天地图的 WMTS 服务（https://t0.tianditu.gov.cn/img_w/wmts?request=GetCapabilities&service=wmts）请求中
    # 标记出了原点位置 <TopLeftCorner>20037508.3427892 -20037508.3427892</TopLeftCorner> 两个值实际就是地球的周长的一半
    # 例如 -20037508.3427892 为左侧起点，那么右侧重点就为 20037508.3427892，整个跨度就是地球周长 4.00750166855784861532e7

    mpp = get_meters_per_pixel(zoom)

    # 与下面方式相同，直接使用地球周长一半：
    # row = math.floor((C / 2 - lat) / (mpp * 256))
    # col = math.floor((lng + C / 2) / (mpp * 256))

    left = -20037508.3427892
    top = 20037508.3427892
    # 理解一下，经度决定列块大小，纬度决定行块大小
    # 公式原理：当前位置与原点位置的偏移量（单位是米），除以每块瓦片的总米数，就是瓦片位置了
    row = math.floor((top - lat) / (mpp * 256))
    col = math.floor((lng - left) / (mpp * 256))

    return (row, col, zoom)


def tianditu_tile_position_to_EPSG3857(row: int, col: int, zoom: int) -> Tuple[float, float]:
    """通过天地图的瓦片图的行号列号获取伪墨卡托 Pseudo-Mercator（EPSG3857）坐标（该经纬度为墨卡托坐标）

    Args:
        row (int): 行号
        col (int): 列号
        zoom (int): 层级

    Returns:
        Tuple[float, float]: 墨卡托坐标元组
    """

    mpp = get_meters_per_pixel(zoom)

    # 与下面方式相同，直接使用地球周长一半：
    # lat = C / 2 - row * (mpp * 256)
    # lng = col * (mpp * 256) - C / 2

    left = -20037508.3427892
    top = 20037508.3427892
    # 反推
    lat = top - row * (mpp * 256)
    lng = left + col * (mpp * 256)

    return (lng, lat)


def tianditu_EPSG4326_to_tile_position(lng: float, lat: float, zoom: int) -> Tuple[int, int, int]:
    """通过经纬度坐标系（EPSG4326）经纬度坐标获取天地图的瓦片图的行号列号

    Args:
        lng (float): 经度
        lat (float): 纬度
        zoom (_type_): 地图层级

    Returns:
        Tuple[int, int, int]: 元组（行号，列号，层级），该计算方式瓦片图索引从0开始
    """
    # 在天地图的 WMTS 服务（https://t0.tianditu.gov.cn/img_c/wmts?request=GetCapabilities&service=wmts）请求中
    # 标记出了原点位置 <TopLeftCorner>90.0 -180.0</TopLeftCorner>
    left = -180.0
    top = 90.0
    # 理解一下，经度决定列块大小，纬度决定行块大小
    row = math.floor((top - lat) / (180 / 2**(zoom - 1)))
    col = math.floor((lng - left) / (360 / (2**zoom)))

    return (row, col, zoom)


def tianditu_tile_position_to_EPSG4326(row: int, col: int, zoom: int) -> Tuple[float, float]:
    """通过天地图的瓦片图的行号列号获取经纬度坐标系（EPSG4326）经纬度坐标

    Args:
        row (int): 行号
        col (int): 列号
        zoom (int): 层级

    Returns:
        Tuple[float, float]: 经纬度坐标元组
    """

    left = -180.0
    top = 90.0
    # 反推
    lat = top - row * (180 / 2**(zoom - 1))
    lng = left + col * (360 / (2**zoom))

    return (lng, lat)


def osm_EPSG4326_to_tile_position(lng: float, lat: float, zoom: int) -> Tuple[int, int, int]:
    """通过经纬度坐标系（EPSG4326）经纬度坐标获取 OSM（OpenStreeMap）瓦片图的行号列号。OSM、GoogleMap 采用 WGS84（EPSG:4326）地理坐标系

    Args:
        lng (float): 经度
        lat (float): 纬度
        zoom (_type_): 地图层级

    Returns:
        Tuple[int, int, int]: 元组（行号，列号，层级）
    """
    lat_radians = math.radians(lat)
    n = 2.0**zoom
    row = int((1.0 - math.asinh(math.tan(lat_radians)) / math.pi) / 2.0 * n)
    col = int((lng + 180.0) / 360.0 * n)

    return (row, col, zoom)


def osm_tile_position_to_EPSG4326(row: int, col: int, zoom: int) -> Tuple[float, float]:
    """通过 OSM（OpenStreeMap）瓦片图的行号列号反推左上角经纬度（EPSG4326）。OSM、GoogleMap 采用 WGS84（EPSG:4326）地理坐标系

    Args:
        row (int): 行号
        col (int): 列号
        zoom (int): 层级

    Returns:
        Tuple[float, float]: 经纬度坐标元组
    """
    n = 2.0**zoom
    lng = col / n * 360.0 - 180.0
    lat_radians = math.atan(math.sinh(math.pi * (1 - 2 * row / n)))
    lat = math.degrees(lat_radians)

    return (lng, lat)


if __name__ == "__main__":
    # 测试经纬度墨卡托互转
    print("===== 测试经纬度墨卡托互转 =====")
    coordinate4326 = (106.58828259, 29.56782092)
    epsg3857 = EPSG4326_to_EPSG3857(*coordinate4326)
    epsg4326 = EPSG3857_to_EPSG4326(*epsg3857)
    print(f"墨卡托坐标: {epsg3857}")
    print(f"经纬度坐标: {epsg4326}")
    print("")
    print("")

    # 测试获取天地图瓦片图行列号
    print("===== 测试天地图 =====")
    tianditu_position4326 = tianditu_EPSG4326_to_tile_position(*epsg4326, 15)
    tianditu_position3857 = tianditu_EPSG3857_to_tile_position(*epsg3857, 15)
    tianditu_coordinate4326 = tianditu_tile_position_to_EPSG4326(*tianditu_position4326)
    tianditu_coordinate3857 = tianditu_tile_position_to_EPSG3857(*tianditu_position3857)
    print(f"天地图经纬度瓦片位置: {tianditu_position4326}")
    print(f"天地图瓦片左上经纬度: {tianditu_coordinate4326}")
    print(
        f"https://t0.tianditu.gov.cn/img_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILECOL={tianditu_position4326[1]}&TILEROW={tianditu_position4326[0]}&TILEMATRIX={tianditu_position4326[2]}&tk=68d166cfe304fa077ff035bed00edc37"
    )
    print("")
    print(f"天地图墨卡托瓦片位置: {tianditu_position3857}")
    print(f"天地图瓦片左上墨卡托: {tianditu_coordinate3857}")
    print(
        f"https://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={tianditu_position3857[1]}&TILEROW={tianditu_position3857[0]}&TILEMATRIX={tianditu_position3857[2]}&tk=68d166cfe304fa077ff035bed00edc37"
    )
    print("")
    print("")

    # # 测试获取 OSM 瓦片图行列号
    # print("===== 测试 OSM =====")
    # osm_position4326 = osm_EPSG4326_to_tile_position(*coordinate4326, 15)
    # print(f"OSM 经纬度瓦片位置: {osm_position4326}")
    # osm_epsg4326 = osm_tile_position_to_EPSG4326(*osm_position4326)
    # print(f"OSM 瓦片反推经纬度: {osm_epsg4326}")
    # print("")
    # print("")

    # print("===== 瓦片图左上角顶点坐标整除测试 =====")
    # print("经纬度坐标测试经纬度值:(106.578369140625, 29.5751953125)")
    # c_row = math.floor(((90.0) - 29.5751953125) / (180 / 2**(15 - 1)))
    # c_col = math.floor((106.578369140625 - (-180.0)) / (360 / (2**15)))
    # print(f"经纬度瓦片整数值:({c_row}, {c_col})")

    # print("墨卡托坐标测试经纬度值:(11864249.782311961, 3448838.7162271086)")
    # x = get_meters_per_pixel(15) * 256
    # w_row = (20037508.3427892 - 3448838.7162271086) / x
    # w_col = (11864249.782311961 - (-20037508.3427892)) / x
    # print(f"墨卡托瓦片整数值:({w_row}, {w_col})")

    mkt = tianditu_tile_position_to_EPSG3857(13563, 26086, 15)
    print(EPSG3857_to_EPSG4326(*mkt))
