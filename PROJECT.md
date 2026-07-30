# 室内地图 3D 真实建模项目 · 总进度文档

> 最后更新：2026-07-30
> 用途：项目全貌 + 进度 + 约束，供跨 Agent 对话时直接粘贴上下文使用
> 主工作文件：`indoor_map_geohub3d.html`（157 KB，单文件，无构建步骤）

---

## 一、项目目标

做一个**高德地图 + Three.js 融合的室内 3D 地图**，核心能力：

1. 在真实高德地图上叠加 3D 商场建筑模型（按真实楼层数 / 层高 / 轮廓尺寸）
2. 支持室内 POI 标注、楼层切换、语义分区着色
3. 用户定位投影（精度色码 + 朝向箭头）
4. 3D 导航路径（CatmullRom 样条 + TubeGeometry + 动画虚线）
5. 建模编辑器：直接在地图上绘制商场轮廓 / 隔墙 / 区域 / POI
6. 全国商场搜索（离线数据库，30 城市 198 个商场）

**系统角色**（prompts/01_system_role.md）：3D Indoor Localization & Modeling Expert，主攻 Three.js / WebGL / WebGPU + 室内定位（BLE/UWB/Wi-Fi RTT/SLAM）。

---

## 二、当前状态（一句话）

✅ 主文件 `indoor_map_geohub3d.html` 可正常运行（浏览器 + HTTP 服务），3D 建筑渲染、楼层导航、全国商场搜索、建模编辑器均可用。
⚠️ 高德 API Key 类型错误，导致**在线 POI 搜索 / 真实地图数据拉取不可用**，目前靠演示数据 + 离线数据库兜底。

---

## 三、关键约束（最重要，先读这个）

| 约束 | 说明 | 影响 |
|------|------|------|
| **高德 Key 类型错误** | 当前 Key `YOUR_AMAP_KEY_HERE` 是「Web 服务 API」（服务端），非「Web 端 JS API」（浏览器端）。调用浏览器端 API 返回 `USERKEY_PLAT_NOMATCH (10009)` | 在线 `PlaceSearch`、真实地图数据均不可用；**全国商场搜索改用离线数据库兜底** |
| **正确 Key 要求** | 需在 console.amap.com 创建「Web 端 JS API」Key，域名白名单加 `localhost` / `127.0.0.1` | 替换 HTML 第 7 行的 `key=YOUR_KEY_HERE`（当前已填错误 Key，需替换） |
| **GeoHUB 数据中心不可用** | geohub.amap.com 的「数据中心」SPA 因后端微应用 API 返回空数据无法渲染，上传能力被阻塞 | 已生成符合格式的 GeoJSON / glTF 数据文件，但**无法自动上传发布**，改为本地演示模式 |
| **运行协议** | `file://` 协议被浏览器安全策略拦截（脚本加载失败），必须走 HTTP | 用 `python -m http.server` 起服务于 8080 端口，访问 `localhost:8080` |
| **JS API 2.0 可用** | 独立室内地图 API 对新用户暂停，但 JS API 2.0 内置 `AMap.IndoorMap` 插件仍可用 | 主文件用 v2.0 |

---

## 四、文件清单

### 主工作文件（唯一需要维护的）
- **`indoor_map_geohub3d.html`** — 157 KB，当前最新成果。含：AMap+Three.js 融合渲染、全国商场搜索、建模编辑器、楼层导航、3D 参数面板。

### 历史版本（已废弃，留作参考，勿改）
- `indoor_map_final.html` — 3D 重构版（68.9 KB）
- `indoor_map_final_backup_20260729_0921.html` — 09-21 备份（37 KB，搜索功能参考样板）
- `indoor_map_geohub.html` — GeoHUB 集成版（71 KB）
- `indoor_map_fast.html` / `indoor_map_debug.html` / `indoor_map_auto.html` / `indoor_map_fixed.html` / `indoor_map_diagnose.html` / `indoor_map_nav.html` / `map_demo.html` / `indoor_map.html` — 早期迭代版本

### 数据文件（`geohub_data/`）
- `国贸中心_geojson.geojson` — 国贸中心楼层 POI（真实经纬度 116.46/39.91，7 层）
- `guomao_indoor_all.gltf` — 完整 7 层 3D 模型
- `B2_geohub.gltf` — 单层模型
- `gen_model.py` / `generate_geohub_models.py` — 模型生成脚本
- `README.md` — 上传 GeoHUB 步骤说明

### 支撑文档
- `prompts/01_system_role.md` — 系统角色设定
- `task_nationwide_mall_20260729.md` — 全国商场搜索记录
- `task_mall_search_20260729.md` — 商场搜索初版
- `task_modeling_editor_20260729.md` — 建模编辑器实现记录
- `indoor_map_geohub_20260729.md` — GeoHUB 集成记录
- `indoor_map_demo_20260728.md` — 早期技术备忘

### 待清理（临时测试脚本，可删）
- `_screenshot.js` / `_debug2.js` — 昨日遗留的 Playwright 测试脚本
- `screenshot_3d_fusion.png` — 截图产物

---

## 五、功能清单（已实现 ✅）

| 功能 | 状态 | 说明 |
|------|------|------|
| 高德地图加载 | ✅ | JS API 2.0，含 `securityJsCode` 处理 |
| AMap + Three.js 融合渲染 | ✅ | 双 Canvas 叠加，Three.js alpha 透明覆盖；模式：amap / 3D / fusion |
| 3D 参数化建筑模型 | ✅ | 楼层数 / 层高 / 宽度 / 深度滑条实时驱动 |
| 真实坐标建筑尺寸 | ✅ | 基于 GeoJSON 真实经纬度计算，非估算 |
| 楼层导航 | ✅ | 左侧 7 层卡片，切换显示对应楼层模型 |
| POI 标注 + 语义着色 | ✅ | 购物蓝 / 餐饮橙 / 娱乐粉 / 停车灰 |
| 用户定位投影 | ✅ | 精度色码（<1m 绿 / 1-3m 黄 / >3m 红）+ 朝向箭头 |
| 3D 导航路径 | ✅ | CatmullRom 样条 + TubeGeometry + 渐变着色 + 动画虚线 |
| 3D 视角控制 | ✅ | 俯视 / 等距 / 正面 / 侧面，lerp 平滑过渡 |
| 全国商场搜索 | ✅ | 离线数据库 198 商场 / 30 城市 + 城市下拉筛选 |
| 预设商场（3 个） | ✅ | 国贸中心 / 三里屯太古里 / 西单大悦城 |
| 建模编辑器 | ✅ | 右侧浮层：绘制外墙/隔墙/区域/POI，4 标签页，项目保存/加载 |
| 演示模式 | ✅ | 无 Key 时自动降级，加载内置国贸中心数据 |
| 在线 PlaceSearch | ❌ | 被 Key 类型错误阻塞（见约束表） |
| GeoHUB 数据上传 | ❌ | 被数据中心 API 阻塞（见约束表） |

---

## 六、核心架构

```
AMap.Map (WebGL Canvas)
  └─ containerToLngLat / lngLatTo3D(lng, lat, floorIdx) 坐标转换
Three.js WebGLRenderer (alpha:true, premultipliedAlpha:false)
  └─ 同一坐标系叠加渲染 3D 建筑
```

- **渲染模式**：`setMode('amap' | 'three' | 'fusion')`
- **演示入口**：`_enterDemoMode` → `initThree → loadDemoGeoData → buildSceneDemoGLTF → bindEvents → setMode('three') → switchFloor`
- **演示数据**：`DEMO_GEOJSON`（国贸中心 7 层 21 POI，真实经纬度）
- **全国商场**：`MALL_DB`（198 条，{city,name,floors,lng,lat,tag,addr}）+ `searchMall()` + `selectMallResult()`
- **建模编辑器**：`edApplyToScene()` 把编辑器数据应用到 Three.js 场景；`localStorage` key `indoor3d_edConfig`

### 初始化顺序（关键，曾在此踩坑）
`window.load` → `initMap()` → `mapObj.on('complete')` 末尾调 `applyGeoJsonToScene(DEMO_GEOJSON)` + `setTimeout(()=>setMode('three'),100)` → `initThree()` 须在 `_enterDemoMode` 前同步调用 → `resize` 监听需 `threeCanvas` 非空保护。

---

## 七、如何运行 / 测试

```powershell
# 启动 HTTP 服务（必须，file:// 会被拦截）
cd "C:\Users\严梓轩\.openclaw\workspace\室内地图项目"
python -m http.server 8080

# 浏览器访问
# http://localhost:8080/室内地图项目/indoor_map_geohub3d.html
```

测试用 Playwright（Edge headless）：
```js
const { chromium } = require('.../playwright-core');
// 启动参数：executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
// 访问后 waitForTimeout(6000~8000) 等地图就绪
```

---

## 八、已知问题 / TODO

1. **替换正确 Key**：拿到「Web 端 JS API」Key 后替换第 7 行，可解锁在线搜索 + 真实数据
2. **GeoHUB 上传**：数据中心 API 恢复后，可上传 `geohub_data/` 下数据并接入
3. **3D 视角 lerp 过渡**：俯视/等距/正面/侧面切换的平滑动画可再打磨
4. **融合模式坐标对齐**：Three.js 与 AMap 坐标对齐需实际真实数据验证
5. **编码问题**：部分早期 .md 文件因 GBK 编码显示乱码，新文档统一 UTF-8
6. **建模编辑器**：POI 拖拽 + TransformControls 集成、glTF 导入后实时替换尚未完全打通

---

## 九、给其他 Agent 的快速上手提示

- 改功能基本都在 `indoor_map_geohub3d.html` 单文件里，搜索函数名即可定位
- 想加商场 → 改 `MALL_DB` 数组（第 ~1107 行附近）
- 想换演示数据 → 改 `DEMO_GEOJSON`
- 卡死先查：`edConfig`/`edPois` 是否缺 `let` 声明、`placeSearch` 是否走 `AMap.plugin` 回调、`threeCanvas` 空引用
- 测试务必走 localhost HTTP，别用 file://
- 截图验证用 Playwright headless + Edge，端口 8080
