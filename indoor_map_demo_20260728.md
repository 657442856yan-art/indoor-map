# 高德室内地图展示 Demo

## 任务目标
基于高德开放平台 JS API 2.0，实现带楼层切换的室内地图展示页面。

## 技术方案
- **平台**: 高德地图 JS API 2.0
- **核心功能**: `AMap.IndoorMap` 室内地图图层
- **关键API**: `indoorMap.showIndoorMap(poiId, floorIndex)` 加载指定建筑的指定楼层
- **事件**: `floorchanged` / `buildingchanged` 监听楼层和建筑切换

## 生成文件
- `C:\Users\严梓轩\.openclaw\workspace\indoor_map.html` — 完整室内地图演示页面

## 核心功能
1. 🏢 **室内地图展示** — 加载指定建筑物的室内平面图
2. 🔢 **楼层切换器** — 右侧垂直楼层按钮，支持快速切换楼层
3. 🏪 **楼层内POI搜索** — 搜索商铺/设施名称，支持高亮
4. 📍 **点击获取坐标** — 点击地图任意处复制经纬度
5. 📋 **信息面板** — 显示建筑名、当前楼层、楼层数量、坐标
6. 🧭 **路线规划入口** — 预留室内导航按钮

## 使用前提
用户需到 [高德控制台](https://console.amap.com/dev/key/app) 申请 Web API Key 并替换文件中的 `YOUR_KEY_HERE`。

室内地图 POI ID `B000A856LJ` 对应北京国贸中心，可替换为任意支持室内地图的建筑。

## 参考文档
- https://lbs.amap.com/api/javascript-api-v2/guide/map/indoor-map
- https://lbs.amap.com/product/indoorintro
