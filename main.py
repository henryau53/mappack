#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
import json
import flask_configs
import core.utils.map as map
import core.tianditu.packer as packer

app = Flask(__name__)
app.config.from_object(flask_configs)


@app.route('/')
def hello():
    return render_template('tianditu.html')


@app.route('/getBoundsOrigins', methods=['post'])
def get_bounds_origins():
    bounds = request.get_json()
    level = int(bounds["zoom"])
    # 计算瓦片坐标
    tile_nw = map.tianditu_EPSG4326_to_tile_position(*bounds["nw"], level)
    tile_ne = map.tianditu_EPSG4326_to_tile_position(*bounds["ne"], level)
    tile_se = map.tianditu_EPSG4326_to_tile_position(*bounds["se"], level)
    tile_sw = map.tianditu_EPSG4326_to_tile_position(*bounds["sw"], level)

    # 计算坐标区域的瓦片四个原点坐标
    coordinate_nw = map.tianditu_tile_position_to_EPSG4326(*tile_nw)
    coordinate_ne = map.tianditu_tile_position_to_EPSG4326(tile_ne[0], tile_ne[1] + 1, tile_ne[2])
    coordinate_se = map.tianditu_tile_position_to_EPSG4326(tile_se[0] + 1, tile_se[1] + 1, tile_se[2])
    coordinate_sw = map.tianditu_tile_position_to_EPSG4326(tile_sw[0] + 1, tile_sw[1], tile_sw[2])

    packer.download_tiles(level, tile_nw[0], tile_sw[0], tile_nw[1], tile_ne[1])
    packer.bundle_tiles(level)
    packer.translate_bundle(level, coordinate_nw, coordinate_se)

    data = {
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

    return json.dumps(data), 200


if __name__ == '__main__':
    app.run()
