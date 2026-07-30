# GeoHUB 3D 模型包 - 北京国贸中心

> 生成时间: 2026-07-29
> 模型格式: glTF 2.0 (.gltf)
> 坐标系: 室内局部坐标系 (原点: 116.4603°E, 39.9093°N)

---

## 文件清单

| 文件 | 说明 | 大小 |
|------|------|------|
| `国贸中心_geojson.geojson` | 楼层 POI 数据（22个标注点+2个区域） | 10 KB |
| `guomao_indoor_all.gltf` | 完整7层合并模型（室内坐标系） | 15 KB |
| `gen_model.py` | 模型生成脚本 | 6 KB |
| `README.md` | 本文件 | -- |

---

## 上传 GeoHUB 步骤

### 第一步：上传 GeoJSON（数据层）

```
1. 打开 https://geohub.amap.com → 登录
2. 左侧菜单 → 「数据中心」→「上传数据」
3. 文件类型选择：GeoJSON
4. 上传文件：「国贸中心_geojson.geojson」
5. 点击发布 → 复制 Data API URL
```

### 第二步：上传 glTF（3D模型层）

```
1. GeoHUB 控制台 → 「数据中心」→「上传数据」
2. 文件类型选择：3D模型 / glTF
3. 上传文件：「guomao_indoor_all.gltf」
4. 发布后获取模型 URL 或 Tileset ID
```

---

## 坐标系说明

GeoHUB glTF 使用**室内局部坐标系**：

```
室内X = (经度 - 116.4603) × 60000   → 范围 0~120 米
室内Z = (纬度  - 39.9093)  × 90000  → 范围 0~90  米
Y轴 = 楼层高度（米）

楼层 → Y坐标映射：
  B2 → 0m
  B1 → 4m
  L1 → 8m
  L2 → 12m
  L3 → 16m
  L4 → 20m
  L5 → 24m
```

---

## 楼层数据摘要

| 楼层ID | Y轴高度 | 类型 | 主要业态 |
|--------|---------|------|---------|
| B2 | 0m | parking | 停车场A区 |
| B1 | 4m | shopping | Ole超市、星巴克 |
| L1 | 8m | shopping | Chanel、Dior、电梯 |
| L2 | 12m | shopping | Gucci、Prada |
| L3 | 16m | shopping | ZARA、UNIQLO、Nike |
| L4 | 20m | dining | 绿茶、外婆家、鼎泰丰 |
| L5 | 24m | entertainment | 休闲娱乐 |

---

## 接入代码（indoor_map_geohub.html）

上传完成后，将 GeoHUB 提供的 API URL 填入网页侧边栏的「GeoHUB Data API URL」输入框，即可将上传的数据注入 Three.js 3D 场景中实时渲染。
