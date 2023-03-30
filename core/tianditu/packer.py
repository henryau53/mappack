#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import glob
import re
from typing import List
from PIL import Image
from core.tianditu import tile_processor
from mappack_configs import TIANDITU_IMG_C_URL, TIANDITU_TILE_PATH, TIANDITU_BUNDLE_PATH, TIANDITU_GEOTIFF_PATH


def download_tiles(level: int, start_row: int, end_row: int, start_col: int, end_col: int) -> None:
    """下载指定层级的所有瓦片图。

    Args:
        level (int): 指定下载层级
        start_row (int): 起始行号
        end_row (int): 终止行号
        start_col (int): 起始列号
        end_col (int): 终止列号
    """
    output_path = os.path.join(TIANDITU_TILE_PATH, str(level))
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
            tile_processor.fetch_tile(TIANDITU_IMG_C_URL, row, col, level, save_as)


def bundle_tiles(level: int) -> None:
    """合并指定层级的瓦片图为大图。

    Args:
        level (int): 指定层级
    """
    row_paths = glob.glob(os.path.join(TIANDITU_TILE_PATH, str(level), "*"))
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

    output_path = os.path.join(TIANDITU_BUNDLE_PATH, str(level))
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")

    output = os.path.join(output_path, "bundle.jpg")
    bundle.save(output, quality=100)
    logging.info(f"生成\033[1;36m{output}\033[0m")


def translate_bundle(level: int, nw: List[float], se: List[float], epsg: str = "EPSG:4326") -> None:
    """转换瓦片合成大图为geotiff。

    Args:
        level (int): 指定大图所属层级
        nw (List[float]): 左上角坐标
        se (List[float]): 右下角坐标
        epsg (str, optional): EPSG串，默认"EPSG:4326"
    """
    input = os.path.join(TIANDITU_BUNDLE_PATH, str(level), "bundle.jpg")
    output_path = os.path.join(TIANDITU_GEOTIFF_PATH, str(level))
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
        logging.info(f"创建\033[1;36m{output_path}\033[0m目录")
    output = os.path.join(output_path, "bundle.tif")
    tile_processor.translate_geotiff(nw, se, input, output, epsg)
    logging.info(f"生成\033[1;36m{output}\033[0m")
