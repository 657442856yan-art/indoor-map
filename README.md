# 室内 3D 地图项目

基于 **高德地图 JS API** + **Three.js** 的室内 3D 地图与自定义建模演示项目。

## 功能特性

- 室外标准地图，点击建筑即可进入 **3D 室内漫游**
- 室内店铺导航与路径规划
- **自定义 3D 建模**：调整楼层尺寸、加内墙隔断、编辑/移动/改色店铺、放置设施（电梯/扶梯/楼梯/喷泉）、自由绘制建筑轮廓、逐层独立编辑
- 内置教程引导与「快速开始」清单，降低上手门槛

## 入口文件

| 文件 | 说明 |
| --- | --- |
| `indoor_map_final_backup_20260729_0921.html` | 完整版（顶部 HUD + 右侧自定义抽屉） |
| `indoor_map_geohub3d.html` | GeoHUB 风格独立建筑建模编辑器版 |

其余 `indoor_map_*.html` 为不同开发阶段的版本，可按需参考。

## 使用前：配置你自己的高德 Key

> ⚠️ **本仓库不含任何真实高德 Key**（已统一替换为占位符），请使用你自己的 Key，避免配额被盗用。

1. 前往 [高德开放平台](https://lbs.amap.com/) 申请 **「Web 端 (JS API)」** 类型的 Key，并配置 **安全密钥 (securityJsCode)**。
2. 在 HTML 文件中，将以下两处占位符替换为你的密钥：
   - `YOUR_AMAP_KEY_HERE` → 你的高德 Key
   - `YOUR_AMAP_SECURITY_CODE` → 你的安全密钥
3. （可选）文档 `PROJECT.md` 等中的 `YOUR_AMAP_KEY_HERE` 同理替换。

> 提示：不同 HTML 顶部引入高德脚本的方式略有差异，请确认每个文件里的 `key=` 与安全密钥都已替换。

## 本地运行

直接用浏览器打开对应 HTML 即可（需联网加载高德地图与 Three.js 的 CDN）。

如遇到浏览器对本地文件的限制，建议用本地静态服务器：

```bash
# 在项目目录下
python -m http.server 8000
# 然后访问 http://localhost:8000/indoor_map_final_backup_20260729_0921.html
```

## 目录说明

- `indoor_map_*.html` —— 各阶段版本
- `geohub_data/` —— GeoHUB 模型（.gltf）、geojson 数据与生成脚本
- `prompts/` —— 使用的提示词
- `PROJECT.md` 等 —— 项目文档与排错记录
- `*.bak` —— 本地含真实密钥的备份（已被 `.gitignore` 排除，不会上传）

## 备注

本地修改前的真实密钥备份保存在各 `*.bak` 文件中（仅本地，不入库）。如需恢复本地可用版本，用对应 `.bak` 覆盖即可。
