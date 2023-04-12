(function () {
  // 获取页面元素
  let infoCenter = document.querySelector("#infoCenter"); // 中心点坐标文本块
  let infoNECoordinate = document.querySelector("#infoNECoordinate"); // 右上坐标文本块
  let infoSWCoordinate = document.querySelector("#infoSWCoordinate"); // 左下坐标文本块
  let infoZoom = document.querySelector("#infoZoom"); // 当前层级文本块
  let infoCurrent = document.querySelector("#infoCurrent"); // 当前坐标文本块
  let showGridline = document.querySelector("#showGridline"); // 是否显示网格复选框
  let showDownloadline = document.querySelector("#showDownloadline"); // 是否显示实际下载区域复选框
  let openSelect = document.querySelector("#openSelect"); // 选择区域按钮
  let clearSelect = document.querySelector("#clearSelect"); // 清楚区域按钮
  let selectedNW = document.querySelector("#selectedNW"); // 区域选择左上坐标文本块
  let selectedNE = document.querySelector("#selectedNE"); // 区域选择右上坐标文本块
  let selectedSE = document.querySelector("#selectedSE"); // 区域选择右下坐标文本块
  let selectedSW = document.querySelector("#selectedSW"); // 区域选择左下坐标文本块
  let selectAllZooms = document.querySelector("#selectAllZooms"); // 下载弹窗全部选择按钮
  let unselectAllZooms = document.querySelector("#unselectAllZooms"); // 下载弹窗取消全选按钮
  let progressContainer = document.querySelector("#progressContainer"); // 下载弹窗进度条容器

  let openDownload = document.querySelector("#openDownload"); // 下载弹窗触发按钮
  let downloadDialog = document.querySelector("#downloadDialog"); // 下载窗口
  let download = document.querySelector("#download"); // 下载窗口中的下载按钮
  let cancelDownload = document.querySelector("#cancelDownload"); // 下载窗口中的取消按钮
  let alertDialog = document.querySelector("#alertDialog"); // 警告弹窗
  let alertMessage = document.querySelector("#alertMessage"); // 警告弹窗信息文本块
  let cancelAlert = document.querySelector("#cancelAlert"); // 警告弹窗中的取消按钮

  let zoomCheckbox = document.getElementsByName("zoomCheckbox"); // 下载弹窗所有层级复选框
  let mapTypes = document.getElementsByName("mapType"); // 地图类型两个复选框

  let options = {
    // token
    token: "71945204e48fec91a7e185f3c2ea1ea0",
    // 初始化层级
    zoom: 15,
    // 最小层级
    minZoom: 1,
    // 最大层级
    maxZoom: 18,
    // 默认中心点（北京天安门）
    center: [116.39088, 39.91157],
    // 是否显示网格
    isGridline: false,

    /****** 伪墨卡托 ******/
    // 影像图地址
    imageWURL:
      "http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 影像注记地址
    ciaWURL:
      "http://t0.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 矢量图地址
    vectorWURL:
      "http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 矢量注记地址
    cvaWURL:
      "http://t0.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",

    /****** 经纬度 ******/
    // 影像图地址
    imageCURL:
      "http://t0.tianditu.gov.cn/img_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 影像注记地址
    ciaCURL:
      "http://t0.tianditu.gov.cn/cia_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 矢量图地址
    vectorCURL:
      "http://t0.tianditu.gov.cn/vec_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
    // 矢量注记地址
    cvaCURL:
      "http://t0.tianditu.gov.cn/cva_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=71945204e48fec91a7e185f3c2ea1ea0",
  };

  // 天地图对象
  let map;
  // 天地图控件
  let mapControl;
  // 天地图瓦片图层对象
  let tileLayer;
  // 天地图注记图层对象
  let annotationLayer;
  // 天地图网格线图层对象
  let gridlineLayer;
  // 天地图矩形绘制工具对象
  let rectangleTool;
  // 当前已经选择了的地图选区
  let currentBounds;
  // 当前地图缩放层级
  let currentZoom = options.zoom;
  // 地图是否正在选择区域的标识
  let isRectangling = false;
  // 下载窗口中记录层级是否全选的标识
  let isAllZooms = false;
  // 是否显示实际下载区域
  let isDownloadline = false;
  // 实际下载区域的绘制对象
  let downloadRectangle = undefined;
  // 当前下载中的所有进度条元素的集合
  let progresses = {};

  /**
   * @description 初始化地图
   * @name initMap
   * @return 无
   */
  function initMap() {
    /****** 初始化地图组件 ******/
    // 初始化天地图瓦片图层
    tileLayer = new T.TileLayer(options.imageCURL, {
      minZoom: options.minZoom,
      maxZoom: options.maxZoom,
    });
    // 初始化天地图注记图层
    annotationLayer = new T.TileLayer(options.ciaCURL, {
      minZoom: options.minZoom,
      maxZoom: options.maxZoom,
    });

    // 初始化天地图网格线图层
    gridlineLayer = new T.GridlineLayer({
      opacity: options.isGridline ? 1 : 0,
      outlineSize: {
        width: 1,
        color: "#fff",
      },
      textSize: {
        ontSize: "14",
        display: true,
        color: "red",
        fontWeight: true,
      },
    });

    mapControl = new T.Control.Zoom();
    mapControl.setPosition(T_ANCHOR_TOP_LEFT);

    //初始化天地图地图对象
    map = new T.Map("map", {
      projection: "EPSG:4326", // 经纬度坐标系，默认墨卡托
      layers: [tileLayer, annotationLayer, gridlineLayer],
    });
    map.centerAndZoom(new T.LngLat(...options.center), options.zoom);
    map.addControl(mapControl);

    rectangleTool = new T.RectangleTool(map);

    /****** 注册地图事件 ******/
    // 注册鼠标滑动事件回调
    map.addEventListener("mousemove", onMapMouseMove);
    // 注册鼠标拖拽地图事件回调
    map.addEventListener("moveend", onMapMouseEnd);
    // 注册地图层级缩放事件回调
    map.addEventListener("zoomend", onMapZoomEnd);
    // 注册矩形绘制事件回调
    rectangleTool.addEventListener("draw", onMapDrawRectangle);
  }

  function onMapMouseMove(e) {
    infoCurrent.innerHTML = `${e.lnglat.getLng().toFixed(6)},${e.lnglat
      .getLat()
      .toFixed(6)}`;
  }

  function onMapMouseEnd(e) {
    let map = e.target;
    let center = map.getCenter();
    let bounds = map.getBounds();
    let ne = bounds.getNorthEast(); //可视区域右上角
    let sw = bounds.getSouthWest(); //可视区域左下角
    infoCenter.innerHTML = `${center.getLng().toFixed(6)},${center
      .getLat()
      .toFixed(6)}`;
    infoNECoordinate.innerHTML = `${ne.getLng().toFixed(6)},${ne
      .getLat()
      .toFixed(6)}`;
    infoSWCoordinate.innerHTML = `${sw.getLng().toFixed(6)},${sw
      .getLat()
      .toFixed(6)}`;
  }

  function onMapZoomEnd(e) {
    currentZoom = e.target.getZoom();
    infoZoom.innerHTML = currentZoom;
  }

  function onMapDrawRectangle(e) {
    currentBounds = e.currentBounds;
    let ne = currentBounds.getNorthEast(); //可视区域右上角
    let sw = currentBounds.getSouthWest(); //可视区域左下角
    // 左上，西北
    selectedNW.innerHTML = `${sw.lng.toFixed(6)},${ne.lat.toFixed(6)}`;
    // 右上，东北
    selectedNE.innerHTML = `${ne.lng.toFixed(6)},${ne.lat.toFixed(6)}`;
    // 右下，东南
    selectedSE.innerHTML = `${ne.lng.toFixed(6)},${sw.lat.toFixed(6)}`;
    // 左下，西南
    selectedSW.innerHTML = `${sw.lng.toFixed(6)},${sw.lat.toFixed(6)}`;

    if (isDownloadline) {
      if (downloadRectangle) removeDownloadline();
      let data = {
        zoom: currentZoom,
        nw: [sw.lng, ne.lat],
        ne: [ne.lng, ne.lat],
        se: [ne.lng, sw.lat],
        sw: [sw.lng, sw.lat],
      };
      drawDownloadline(data);
    }

    isRectangling = !isRectangling;
    openSelect.innerHTML = "选择区域";
    openSelect.className = "nes-btn is-success";
    rectangleTool.close();
  }

  /**
   * @description 初始化Dom元素
   * @name initDom
   * @return 无
   */
  function initDom() {
    // 初始化面板信息块
    let center = map.getCenter();
    let bounds = map.getBounds();
    let ne = bounds.getNorthEast(); //可视区域右上角
    let sw = bounds.getSouthWest(); //可视区域左下角
    infoCurrent.innerHTML = `${center.getLng().toFixed(6)},${center
      .getLat()
      .toFixed(6)}`;
    infoCenter.innerHTML = `${center.getLng().toFixed(6)},${center
      .getLat()
      .toFixed(6)}`;
    infoNECoordinate.innerHTML = `${ne.getLng().toFixed(6)},${ne
      .getLat()
      .toFixed(6)}`;
    infoSWCoordinate.innerHTML = `${sw.getLng().toFixed(6)},${sw
      .getLat()
      .toFixed(6)}`;
    infoZoom.innerHTML = map.getZoom();
  }

  /**
   * @description 初始化Dom元素事件
   * @name initDomEvent
   * @return 无
   */
  function initDomEvent() {
    mapTypes.forEach((radio) => {
      radio.addEventListener("change", onDomChageMapType);
    });
    showGridline.addEventListener("change", onDomShowGridline);
    showDownloadline.addEventListener("change", onDomDownloadline);
    openSelect.addEventListener("click", onDomOpenSelect);
    clearSelect.addEventListener("click", onDomClearSelect);
    selectAllZooms.addEventListener("click", onDomSelectALl);
    unselectAllZooms.addEventListener("click", onDomUnselectALl);
    openDownload.addEventListener("click", onOpenDownloadDialog);
    download.addEventListener("click", onDownload);
    cancelDownload.addEventListener("click", onCancelDownload);
    cancelAlert.addEventListener("click", onCancelAlert);
  }

  function onDomChageMapType(e) {
    let tileUrl, annotationUrl;
    switch (e.target.value) {
      case "image":
        tileUrl = options.imageCURL;
        annotationUrl = options.ciaCURL;
        break;
      case "vector":
        tileUrl = options.vectorCURL;
        annotationUrl = options.cvaCURL;
        break;
    }
    tileLayer.setUrl(tileUrl);
    annotationLayer.setUrl(annotationUrl);
  }

  function onDomShowGridline(e) {
    e.target.checked
      ? gridlineLayer.setOpacity(1)
      : gridlineLayer.setOpacity(0);
  }

  function onDomDownloadline(e) {
    isDownloadline = e.target.checked;
    if (isDownloadline && currentBounds) {
      let ne = currentBounds.getNorthEast(); //可视区域右上角
      let sw = currentBounds.getSouthWest(); //可视区域左下角
      let data = {
        zoom: currentZoom,
        nw: [sw.lng, ne.lat],
        ne: [ne.lng, ne.lat],
        se: [ne.lng, sw.lat],
        sw: [sw.lng, sw.lat],
      };
      drawDownloadline(data);
    } else if (!isDownloadline && downloadRectangle) removeDownloadline();
  }

  function onDomOpenSelect(e) {
    isRectangling = !isRectangling;
    if (isRectangling) {
      openSelect.innerHTML = "取消选择";
      openSelect.className = "nes-btn is-error";
      if (downloadRectangle) removeDownloadline();
      currentBounds = undefined;
      rectangleTool.clear();
      rectangleTool.open();
    } else {
      openSelect.innerHTML = "选择区域";
      openSelect.className = "nes-btn is-success";
      rectangleTool.close();
    }
  }

  function onDomClearSelect(e) {
    rectangleTool.clear();
    currentBounds = undefined;
    if (downloadRectangle) removeDownloadline();
  }

  function onDomSelectALl(e) {
    isAllZooms = true;
    zoomCheckbox.forEach((i) => (i.checked = true));
  }

  function onDomUnselectALl(e) {
    isAllZooms = false;
    zoomCheckbox.forEach((i) => (i.checked = false));
  }

  function onOpenDownloadDialog(e) {
    if (currentBounds) {
      downloadDialog.style.display = "flex";
    } else {
      alertDialog.style.display = "flex";
      alertMessage.innerHTML = "对不起，请先选择需要下载的区域";
    }
  }

  function onCancelDownload(e) {
    downloadDialog.style.display = "none";
    onDomUnselectALl();
  }

  function onDownload() {
    if (currentBounds) {
      let ne = currentBounds.getNorthEast(); //可视区域右上角
      let sw = currentBounds.getSouthWest(); //可视区域左下角

      let data = {
        nw: [sw.lng, ne.lat],
        ne: [ne.lng, ne.lat],
        se: [ne.lng, sw.lat],
        sw: [sw.lng, sw.lat],
      };

      let levels = [];
      progresses = {};
      zoomCheckbox.forEach((i) => {
        if (i.checked) {
          levels.push(i.value);
          progresses[i.value] = createProgressElement(`${i.value}级 （0%）`);
          progressContainer.appendChild(progresses[i.value]);
        }
      });

      levels.forEach((level) => {
        data.zoom = level * 1;
        data.uuid = generateUUID(16, 16);

        doDownloadTiles(data);
        doTrackProgress(data.uuid);
      });
    } else throw new Error("下载错误，未选择下载区域");
  }

  function onCancelAlert(e) {
    alertDialog.style.display = "none";
  }

  window.onload = () => {
    initMap();
    initDom();
    initDomEvent();
  };

  function doDownloadTiles(data) {
    let xhr = new XMLHttpRequest();
    // NOTE 同步请求相当于单线程，后台顺序执行。异步相当于多线程，后台同时处理多个请求处理
    xhr.open("post", `/download/tiles`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      // 0:表示没有初始化，说明还没有创建对象
      // 1:表示已经创建对象但是，还没有发送请求
      // 2:表示已经发送，对方已经收到消息了，但是还没有彻底看懂我们什么意思，还有很多事情需要准备
      // 3:服务器已经在给我们响应信息了，但是信息不完整
      // 4:数据已经完整了，可以接收到完整的数据了
      if (xhr.readyState === 4 && xhr.status === 200) {
        let result = JSON.parse(xhr.responseText);
      }
    };
    xhr.send(JSON.stringify(data));
  }

  function doTrackProgress(uuid) {
    let progressTimer = setInterval(() => {
      let xhr = new XMLHttpRequest();
      xhr.open("get", `/download/progress/${uuid}`, true);
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          let result = JSON.parse(xhr.responseText);
          let { current, total, level } = result.data;
          let percent = ((current / total) * 100).toFixed(2);
          let [valueElement, barElement] = progresses[level].children;
          barElement.style.width = `${percent}%`;
          valueElement.innerHTML = `${level}级 （${percent}%）`;
          if (current == total) doDeleteDownloadTaskCache(uuid, progressTimer);
        }
      };
      xhr.send();
    }, 1000);
  }

  function doDeleteDownloadTaskCache(uuid, timmer) {
    let xhr = new XMLHttpRequest();
    xhr.open("delete", `/download/progress/${uuid}`, true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        clearInterval(timmer);
      }
    };
    xhr.send();
  }

  function createProgressElement(label) {
    // dom 模板
    // <div class="progress-bar">
    //   <div id="progressValue" class="value">
    //     18级别 (10%)
    //   </div>
    //   <div id="progressBar" class="bar"></div>
    // </div>
    let progress = document.createElement("div");
    let progressValue = document.createElement("div");
    let progressBar = document.createElement("div");
    progress.className = "progress-bar";
    progressValue.className = "value";
    progressBar.className = "bar";
    progressValue.innerHTML = label;
    progress.appendChild(progressValue);
    progress.appendChild(progressBar);
    return progress;
  }

  function drawDownloadline(data) {
    let xhr = new XMLHttpRequest();
    xhr.open("post", `/info/rectangle`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        let result = JSON.parse(xhr.responseText);
        let bounds = new T.LngLatBounds(
          new T.LngLat(...result.data.coordinate.sw),
          new T.LngLat(...result.data.coordinate.ne)
        );
        downloadRectangle = new T.Rectangle(bounds, {
          color: "#FF0000",
          fillColor: "#FFFFFF",
          fillOpacity: 0,
          lineStyle: "dashed",
        });
        map.addOverLay(downloadRectangle);
      }
    };
    xhr.send(JSON.stringify(data));
  }

  function removeDownloadline() {
    map.removeOverLay(downloadRectangle);
    downloadRectangle = undefined;
  }
})();
