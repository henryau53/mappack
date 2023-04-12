# Mappack 瓦片图打包工具



## 描述

基于`Python Flask`的地图瓦片图打包工具。

> 当前版本仅支持`EPSG4326`经纬度坐标系的天地图。



## 特色

- 瓦片图下载，下载后可供服务器发布目录索引方式的离线地图。
- 瓦片图大图合成，自动将下载的瓦片图合成完整地图图像。
- 地图图像转换，将合成的完整地图图像转换为`Geotiff`格式的图像文件，适用于发布`geoserver`。



## 运行

```bash
# 进入目录
cd mappack

# 安装项目依赖
pip install -r ./requirements.txt

# 启动Flask
python ./main.py

# 浏览器浏览
http://localhost:5000/
```



## 截图

![截图1](./docs/screenshot_1.png)

![截图1](./docs/screenshot_2.png)