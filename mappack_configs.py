#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import logging

# 项目console日志等级
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(funcName)s]: %(message)s")

# -----< 通用配置 >-----
# 项目根目录
BASE_DIR = os.path.abspath('.')

# 通用 User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
]

# -----< 天地图配置 >-----
# 天地图tocken
TIANDITU_TOKEN = "71945204e48fec91a7e185f3c2ea1ea0"

# 天地图瓦片下载目录
TIANDITU_TILE_PATH = os.path.join(BASE_DIR, "dist/tianditu/tile")

# 天地图瓦片合成大图放置目录
TIANDITU_BUNDLE_PATH = os.path.join(BASE_DIR, "dist/tianditu/bundle")

# 天地图GeoTiff放置目录
TIANDITU_GEOTIFF_PATH = os.path.join(BASE_DIR, "dist/tianditu/geotiff")

# 天地图经纬度投影目录前缀
TIANDITU_DIRECTORY = {
    "EPSG:4326": "epsg4326",
    "EPSG:3857": "epsg3857",
    "EPSG:900913": "epsg3857",
    "img": "img",
    "vec": "vec",
}

# 天地图瓦片请求url
TIANDITU_URL = {
    "EPSG:4326": {
        "img":
            f"http://t0.tianditu.gov.cn/img_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}",
        "vec":
            f"http://t0.tianditu.gov.cn/vec_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}"
    },
    "EPSG:3857": {
        "img":
            f"http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}",
        "vec":
            f"http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}"
    },
    "EPSG:900913": {
        "img":
            f"http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}",
        "vec":
            f"http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX=%s&TILEROW=%s&TILECOL=%s&tk={TIANDITU_TOKEN}"
    }
}
