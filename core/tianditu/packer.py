#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import glob
import re
from typing import List
from PIL import Image
from core.tianditu import tile_processor
from mappack_configs import TIANDITU_DIRECTORY, TIANDITU_TILE_PATH, TIANDITU_BUNDLE_PATH, TIANDITU_GEOTIFF_PATH, TIANDITU_URL


def download_tile(zoom: int, row: int, col: int, map_type: str, epsg_code: str) -> bool:
    """单独下载瓦片图，返回是否成功

    Args:
        zoom (int): 瓦片图的层级
        row (int): 瓦片图的行号
        col (int): 瓦片图的列号
        map_type (str): 地图类型，img|vec
        epsg_code (str): EPSG代码，EPSG:4326|EPSG:3857|EPSG:900913

    Returns:
        bool: 成功返回True，失败返回False
    """
    tile_path = os.path.join(TIANDITU_TILE_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    output_path = os.path.join(tile_path, str(zoom), str(row))
    # 创建瓦片存放的层级目录
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")

    save_as = os.path.join(output_path, f"{col}.jpg")
    return tile_processor.fetch_tile(TIANDITU_URL[epsg_code][map_type], row, col, zoom, save_as)


def download_tiles(zoom: int, start_row: int, end_row: int, start_col: int, end_col: int, map_type: str,
                   epsg_code: str) -> None:
    """下载指定层级的所有瓦片图。

    Args:
        zoom (int): 指定下载层级
        start_row (int): 起始行号
        end_row (int): 终止行号
        start_col (int): 起始列号
        end_col (int): 终止列号
        map_type (str): 地图类型，img|vec
        epsg_code (str): EPSG代码，EPSG:4326|EPSG:3857|EPSG:900913
    """
    tile_path = os.path.join(TIANDITU_TILE_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    output_path = os.path.join(tile_path, str(zoom))
    # 创建瓦片存放的层级目录
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")

    for row in range(start_row, end_row + 1):
        # 创建瓦片存放的行级目录
        row_path = os.path.join(output_path, str(row))
        if not os.path.isdir(row_path):
            os.mkdir(row_path)
            logging.info(f"创建\033[1;36m{row_path}\033[0m目录")

        for col in range(start_col, end_col + 1):
            # TODO: 已经在fetch_tile中加入成功失败返回参数，回头可以添加失败重试
            save_as = os.path.join(row_path, f"{col}.jpg")
            tile_processor.fetch_tile(TIANDITU_URL[epsg_code][map_type], row, col, zoom, save_as)


def bundle_tiles(zoom: int, map_type: str, epsg_code: str) -> None:
    """合并指定层级的瓦片图为大图。

    Args:
        zoom (int): 指定层级
        map_type (str): 地图类型，img|vec
        epsg_code (str): EPSG代码，EPSG:4326|EPSG:3857|EPSG:900913
    """
    tile_path = os.path.join(TIANDITU_TILE_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    bundle_path = os.path.join(TIANDITU_BUNDLE_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    row_paths = glob.glob(os.path.join(tile_path, str(zoom), "*"))
    row_paths.sort(key=lambda i: int(re.search(r"/(\d+)$", i).group(1)))
    tiles = []
    for row_path in row_paths:
        jpegs = glob.glob(os.path.join(row_path, "*.jpg"))
        jpegs.sort(key=lambda j: int(re.search(r"/(\d+)\.jpg", j).group(1)))
        tiles.append(jpegs)

    width = max([len(i) for i in tiles]) * 256
    height = len(tiles) * 256
    bundle = Image.new("RGB", (width, height))

    offset_y = 0
    for row_tiles in tiles:
        offset_x = 0
        chunks = list(map(Image.open, row_tiles))
        for chunk in chunks:
            bundle.paste(chunk, (offset_x, offset_y))
            offset_x += chunk.width
        offset_y += chunks[0].height

    output_path = os.path.join(bundle_path, str(zoom))
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")

    output = os.path.join(output_path, "bundle.jpg")
    bundle.save(output, quality=100)
    logging.info(f"生成\033[1;36m{output}\033[0m")


def translate_bundle(zoom: int, nw: List[float], se: List[float], map_type: str, epsg_code: str) -> None:
    """转换瓦片合成大图为geotiff。

    Args:
        zoom (int): 指定大图所属层级
        nw (List[float]): 左上角坐标
        se (List[float]): 右下角坐标
        map_type (str): 地图类型，img|vec
        epsg_code (str): EPSG代码，EPSG:4326|EPSG:3857|EPSG:900913
    """
    bundle_path = os.path.join(TIANDITU_BUNDLE_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    geotiff_path = os.path.join(TIANDITU_GEOTIFF_PATH, TIANDITU_DIRECTORY[epsg_code], TIANDITU_DIRECTORY[map_type])
    input = os.path.join(bundle_path, str(zoom), "bundle.jpg")
    output_path = os.path.join(geotiff_path, str(zoom))
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")
    output = os.path.join(output_path, "bundle.tif")
    tile_processor.translate_geotiff(nw, se, input, output, epsg_code)
    logging.info(f"生成\033[1;36m{output}\033[0m")
