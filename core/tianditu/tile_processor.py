#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
from typing import List
import urllib3
import logging
from osgeo import gdal, osr
from core.constants import EPSG4326
from mappack_configs import USER_AGENTS

manager = urllib3.PoolManager(timeout=5.0, retries=3, num_pools=256)


def fetch_tile(url: str, row: int, col: int, zoom: int, save_as: str) -> bool:
    """根据指定的下载地址下载并保存指定的瓦片图。

    Args:
        url (str): 瓦片图下载地址
        row (int): 瓦片图所属行号
        col (int): 瓦片图所属列号
        zoom (int): 瓦片图层级
        save_as (str): 保存的文件路径与名称

    Returns:
        bool: 成功返回True，失败返回False
    """
    tile_url = url % (zoom, row, col)
    response = manager.request("GET", tile_url, headers={"User-Agent": random.choice(USER_AGENTS)})
    logging.debug(f"瓦片地址：{tile_url}")
    if response.data:
        logging.info(f"\033[1;36m获取{row}行，{col}列瓦片图成功\033[0m")
        with open(save_as, "wb") as file:
            file.write(response.data)
        return True
    else:
        logging.error(f"\033[1;31m获取{row}行，{col}列瓦片图失败\033[0m")
        return False


def translate_geotiff(nw: List[float], se: List[float], input: str, output: str, epsg: str = EPSG4326) -> None:
    """转换图片为geotiff格式，实际将空间信息加入到图片中。

    Args:
        nw (List[float]): 左上角坐标
        se (List[float]): 右下角坐标
        input (str): 输入文件路径，即待转换源
        output (str): 输出文件路径，即转换后的图片
        epsg (str, 可选): EPSG串，默认"EPSG:4326"
    """
    dataset = gdal.Open(input)
    if dataset is None:
        logging.error(f"\033[1;31m{input}文件不存在\033[0m")
        return

    # 创建空间索引
    srs = osr.SpatialReference()
    # 设置空间的坐标系
    srs.ImportFromEPSG(int(epsg.split(":")[1]))

    # 创建仿射变换元组，参数说明：
    # 左上角经度
    # 水平分辨率（该分辨率为像素分辨率，为每像素代表多少个坐标系单位（比如度，米））
    # 水平旋转参数，正北为0
    # 左上角纬度
    # 垂直旋转参数，正北为0
    # 垂直分辨率，同水平分辨率（注意需要负值）
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    h_resolution = (se[0] - nw[0]) / width
    v_resolution = (se[1] - nw[1]) / height
    geo_transform = (nw[0], h_resolution, 0, nw[1], 0, v_resolution)
    # 设置仿射变换
    dataset.SetGeoTransform(geo_transform)
    # 设置坐标系
    dataset.SetProjection(srs.ExportToWkt())
    gdal.Translate(output, dataset, format="GTiff")


def translate_geotiff_gcp(nw: List[float],
                          ne: List[float],
                          se: List[float],
                          sw: List[float],
                          input: str,
                          output: str,
                          epsg: str = EPSG4326) -> None:
    """转换图片为geotiff格式，实际将空间信息加入到图片中，此方式使用空间信息校正方式。

    Args:
        nw (List[float]): 左上角坐标
        ne (List[float]): 右上角坐标
        se (List[float]): 右下角坐标
        sw (List[float]): 左下角坐标
        input (str): 输入文件路径，即待转换源
        output (str): 输出文件路径，即转换后的图片
        epsg (str, optional): EPSG串，默认"EPSG:4326"
    """
    dataset = gdal.Open(input)
    if dataset is None:
        logging.error(f"\033[1;31m{input}文件不存在\033[0m")
        return
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    gcp_meta = [[*nw, 0, 0], [*ne, width - 1, 0], [*se, width - 1, height - 1], [*sw, 0, height - 1]]
    gcps = []
    for item in gcp_meta:
        x, y, pixel, line = item
        z = 0
        gcps.append(gdal.GCP(x, y, z, pixel, line))

    options = gdal.TranslateOptions(format="GTiff", outputSRS=epsg, GCPs=gcps)
    gdal.Translate(output, dataset, options=options)
