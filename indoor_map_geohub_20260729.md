# GeoHUB 集成版室内地图 · 任务记录

**时间**: 2026-07-29 10:04
**文件**: indoor_map_geohub.html (72,688 bytes)
**状态**: ✅ 已完成

---

## GeoHUB 两大核心模块

### 1. Style Studio（样式工作室）
- 访问: https://geohub.amap.com → 样式 → 创建样式
- 输出: `amap://styles/xxxxxxxx` 格式的 Style ID
- 代码接入: `map.setMapStyle('amap://styles/xxxxxxxx')`
- 内置 6 种官方样式: 默认、深蓝夜色、浅色亮丽、午夜深紫、简约灰白、自然清新

### 2. Data Hub（地图数据中心）
- 访问: https://geohub.amap.com → 数据中心 → 上传数据
- 支持格式: GeoJSON FeatureCollection / CSV
- 发布后获取 API URL，代码中 `fetch(URL)` 注入 POI 数据
- 注入后数据直接用于 Three.js 楼层 POI 标注

---

## 代码集成的三个层面

### 地图样式 (setMapStyle)
```javascript
// GeoHUB Style ID 接入
const styleId = document.getElementById('geohubStyleId').value.trim();
map.setMapStyle(styleId.startsWith('amap://') ? styleId : `amap://styles/${styleId}`);
```

### GeoHUB Data API 接入
```javascript
// Data Hub API 调用
const resp = await fetch('https://restapi.geohub.amap.com/v1/data/...');
const data = await resp.json();
// data.features[].geometry.coordinates → lngLatTo3D() → Three.js
```

### 本地 GeoJSON 上传（绕过 API）
```javascript
// 支持用户直接上传 GeoJSON 文件
// 格式: {"type":"FeatureCollection","features":[...]}
// properties: name, floor, type (shopping/dining/entertainment/parking)
// geometry: {"type":"Point","coordinates":[lng, lat]}
```

---

## 三视图模式

| 模式 | 说明 |
|------|------|
| 📍 地图 | 纯 AMap，IndoorMap 插件楼层 |
| 🏗️ 3D | 纯 Three.js，可拖拽旋转/缩放 |
| ⚡ 融合 | AMap底图 + Three.js半透明叠加层，相机联动 |

---

## Three.js 融合渲染架构

```
AMap.Map (WebGL Canvas)
    ↓ containerToLngLat 坐标转换
    ↓ lngLatTo3D(lng, lat, floorIdx)
Three.js WebGLRenderer (alpha:true, premultipliedAlpha:false)
    ↓ 同一坐标系
语义着色: 购物=蓝 / 餐饮=橙 / 娱乐=粉 / 停车=灰
```

## 访问
http://localhost:8080/室内地图项目/indoor_map_geohub.html
