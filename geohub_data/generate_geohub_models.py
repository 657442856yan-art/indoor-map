"""
GeoHUB 3D 模型生成脚本
生成 glTF 2.0 格式楼层模型，可直接上传到 GeoHUB Data Hub
"""
import json
import struct
import base64
import os
from pathlib import Path

PY = r"C:\Program Files\QClaw\v0.2.35.624\resources\python\python.exe"
import sys
sys.path.insert(0, r"C:\Users\严梓轩\AppData\Roaming\Python\Python311\Lib\site-packages")
import trimesh
import numpy as np

OUT = Path(r"C:\Users\严梓轩\.openclaw\workspace\室内地图项目\geohub_data")
OUT.mkdir(exist_ok=True)

# 国贸中心楼层配置
# 坐标范围: lng 116.4603~116.4615, lat 39.9093~39.9102
# 室内坐标系: x 0~120, z 0~90 (单位: 米)
# 经纬度转室内: x = (lng - 116.4603) * 60000, z = (lat - 39.9093) * 90000

def ll_to_indoor(lng, lat):
    return (lng - 116.4603) * 60000, (lat - 39.9093) * 90000

FLOORS = [
    {"id": "B2", "name": "B2层 - 停车场A区", "y": 0, "color": [0.12, 0.16, 0.22], "alpha": 0.9,
     "type": "parking", "features": []},
    {"id": "B1", "name": "B1层 - 超市/轻食", "y": 4, "color": [0.06, 0.20, 0.30], "alpha": 0.9,
     "type": "shopping", "features": [
         {"x": 36, "z": 27, "w": 28, "d": 20, "type": "shop", "name": "Ole超市"},
         {"x": 72, "z": 18, "w": 18, "d": 14, "type": "shop", "name": "星巴克"},
    ]},
    {"id": "L1", "name": "L1层 - 奢侈品/美妆", "y": 8, "color": [0.12, 0.25, 0.50], "alpha": 0.9,
     "type": "shopping", "features": [
         {"x": 20, "z": 40, "w": 18, "d": 16, "type": "shop", "name": "Chanel"},
         {"x": 60, "z": 45, "w": 18, "d": 14, "type": "shop", "name": "Dior"},
         {"x": 95, "z": 30, "w": 16, "d": 12, "type": "elevator", "name": "电梯A"},
         {"x": 10, "z": 50, "w": 14, "d": 10, "type": "entrance", "name": "东门"},
         {"x": 110, "z": 50, "w": 14, "d": 10, "type": "exit", "name": "西门"},
    ]},
    {"id": "L2", "name": "L2层 - 国际大牌", "y": 12, "color": [0.06, 0.15, 0.40], "alpha": 0.9,
     "type": "shopping", "features": [
         {"x": 22, "z": 35, "w": 22, "d": 18, "type": "shop", "name": "Gucci"},
         {"x": 60, "z": 40, "w": 20, "d": 16, "type": "shop", "name": "Prada"},
    ]},
    {"id": "L3", "name": "L3层 - 时尚服饰", "y": 16, "color": [0.10, 0.30, 0.70], "alpha": 0.9,
     "type": "shopping", "features": [
         {"x": 18, "z": 36, "w": 20, "d": 16, "type": "shop", "name": "ZARA"},
         {"x": 55, "z": 42, "w": 20, "d": 16, "type": "shop", "name": "UNIQLO"},
         {"x": 88, "z": 36, "w": 18, "d": 14, "type": "shop", "name": "Nike"},
    ]},
    {"id": "L4", "name": "L4层 - 美食广场", "y": 20, "color": [0.50, 0.30, 0.05], "alpha": 0.9,
     "type": "dining", "features": [
         {"x": 20, "z": 36, "w": 24, "d": 20, "type": "shop", "name": "绿茶餐厅"},
         {"x": 60, "z": 30, "w": 20, "d": 16, "type": "shop", "name": "外婆家"},
         {"x": 90, "z": 42, "w": 16, "d": 14, "type": "shop", "name": "鼎泰丰"},
    ]},
    {"id": "L5", "name": "L5层 - 休闲娱乐", "y": 24, "color": [0.40, 0.10, 0.45], "alpha": 0.9,
     "type": "entertainment", "features": []},
]

def make_floor_mesh(floor, ceil=False):
    """生成单层楼板 mesh"""
    h = 0.3
    y_offset = floor["y"] + (h if ceil else 0)
    
    # 主体楼板
    floor_mesh = trimesh.creation.box(
        extents=[120, h, 90],
        transform=trimesh.transformations.translation_matrix([60, y_offset, 45])
    )
    
    # 分割线网格
    grid_mesh = trimesh.creation.grid_in_box(
        bounds=[[0, y_offset, 0], [120, y_offset + h, 90]],
        pitch=[10, 10],
        color=[0.2, 0.2, 0.25, 0.3]
    ) if False else None  # 简化，暂不添加
    
    meshes = [floor_mesh]
    
    # 业态功能区色块
    type_colors = {
        "shop": [0.1, 0.3, 0.7, 0.7],   # 蓝
        "dining": [0.7, 0.4, 0.1, 0.7],  # 橙
        "elevator": [0.8, 0.1, 0.8, 0.6], # 紫
        "entrance": [0.1, 0.7, 0.3, 0.6], # 绿
        "exit": [0.8, 0.1, 0.1, 0.6],    # 红
        "toilet": [0.1, 0.5, 0.6, 0.6],  # 青
    }
    
    for feat in floor.get("features", []):
        col = type_colors.get(feat["type"], [0.3, 0.3, 0.3, 0.6])
        box = trimesh.creation.box(
            extents=[feat["w"], 0.5, feat["d"]],
            transform=trimesh.transformations.translation_matrix([
                feat["x"] + feat["w"]/2,
                floor["y"] + 0.4,
                feat["z"] + feat["d"]/2
            ])
        )
        # 简单着色
        box.visual.vertex_colors = [
            int(c * 255) for c in col
        ] * len(box.visual.vertex_colors)
        meshes.append(box)
    
    # 边界墙
    wall_h = 3.5
    wall_t = 0.5
    wall_col = [floor["color"][0] * 1.3, floor["color"][1] * 1.3, floor["color"][2] * 1.3, 0.5]
    walls = [
        ([60, floor["y"] + wall_h/2, 0], [120, wall_h, wall_t]),
        ([60, floor["y"] + wall_h/2, 90], [120, wall_h, wall_t]),
        ([0, floor["y"] + wall_h/2, 45], [wall_t, wall_h, 90]),
        ([120, floor["y"] + wall_h/2, 45], [wall_t, wall_h, 90]),
    ]
    for (cx, cy, cz), (ex, ey, ez) in walls:
        wm = trimesh.creation.box(
            extents=[ex, ey, ez],
            transform=trimesh.transformations.translation_matrix([cx, cy, cz])
        )
        meshes.append(wm)
    
    return trimesh.util.concatenate(meshes)


def make_glTF(scene_or_mesh, out_path, name, metadata=None):
    """导出为 glTF 2.0 JSON 格式（GeoHUB 兼容）"""
    
    # 合并几何
    if hasattr(scene_or_mesh, 'sections'):
        meshes = scene_or_mesh.dump(True)
    else:
        meshes = [scene_or_mesh]
    
    # 去重重复几何
    unique = []
    seen = set()
    for m in meshes:
        key = m.visual.kind if hasattr(m, 'visual') else 'none'
        if key not in seen:
            seen.add(key)
            unique.append(m)
    meshes = unique

    all_vertices = []
    all_normals = []
    all_colors = []
    all_indices = []
    base_idx = 0

    for m in meshes:
        # 提取顶点
        verts = np.array(m.vertices).flatten()
        normals = np.array(m.vertex_normals).flatten() if len(m.vertex_normals) == len(m.vertices) else np.zeros(len(verts))
        
        # 提取颜色
        if hasattr(m.visual, 'vertex_colors') and len(m.visual.vertex_colors) > 0:
            vc = np.array(m.visual.vertex_colors)[:, :4] / 255.0
            colors = np.tile(vc.mean(axis=0), (len(m.vertices), 1)).flatten()
        else:
            colors = np.tile([0.5, 0.5, 0.6, 0.9], len(m.vertices))
        
        # 提取索引
        if hasattr(m, 'faces'):
            idx = np.array(m.faces).flatten()
        elif hasattr(m, 'elements') and m.element_type == 'face':
            idx = np.array(m.elements).flatten()
        else:
            idx = np.arange(len(verts)//3, dtype=np.uint32)
        
        all_vertices.extend(verts.tolist())
        all_normals.extend(normals.tolist())
        all_colors.extend(colors.tolist())
        all_indices.extend((idx + base_idx).tolist())
        base_idx += len(verts) // 3

    vertices_b64 = base64.b64encode(struct.pack(f'<{len(all_vertices)}f', *all_vertices)).decode()
    normals_b64  = base64.b64encode(struct.pack(f'<{len(all_normals)}f', *all_normals)).decode()
    colors_b64  = base64.b64encode(struct.pack(f'<{len(all_colors)}f', *all_colors)).decode()
    indices_b64 = base64.b64encode(struct.pack(f'<{len(all_indices)}I', *all_indices)).decode()

    v_count = len(all_vertices) // 3
    i_count = len(all_indices)

    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "GeoHUB-Indoor-Model-Generator v1.0",
            "copyright": "Generated by QClaw Agent"
        },
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{
            "name": name,
            "primitives": [{
                "attributes": {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2},
                "indices": 3,
                "material": 0,
                "mode": 4
            }]
        }],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": v_count, "type": "VEC3", "max": [120, 27, 90], "min": [0, 0, 0]},
            {"bufferView": 1, "componentType": 5126, "count": v_count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": v_count, "type": "VEC4"},
            {"bufferView": 3, "componentType": 5125, "count": i_count, "type": "SCALAR"}
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0,        "byteLength": len(all_vertices)*4, "target": 34962},
            {"buffer": 0, "byteOffset": len(all_vertices)*4, "byteLength": len(all_normals)*4, "target": 34962},
            {"buffer": 0, "byteOffset": len(all_vertices)*4*2, "byteLength": len(all_colors)*4, "target": 34962},
            {"buffer": 0, "byteOffset": len(all_vertices)*4*3, "byteLength": len(all_indices)*4, "target": 34963}
        ],
        "buffers": [{
            "byteLength": len(all_vertices)*4*4 + len(all_indices)*4,
            "uri": f"data:model/gltf;base64,{vertices_b64}{normals_b64}{colors_b64}{indices_b64}"
        }],
        "materials": [{
            "name": f"{name}_mat",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.8, 0.8, 0.85, 0.9],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.7
            },
            "alphaMode": "BLEND",
            "doubleSided": True
        }]
    }
    
    if metadata:
        gltf["extras"] = metadata
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(gltf, f, indent=2, ensure_ascii=False)
    
    return out_path


def generate_3dtileset_json(out_path, building_name, building_id):
    """生成 3D Tiles JSON（GeoHUB 3D Tileset 描述文件）"""
    tileset = {
        "asset": {
            "version": "1.0",
            "tilesetVersion": "1.0",
            "generator": "GeoHUB-Indoor-Model-Generator",
            "name": building_name,
            "description": f"室内3D楼层模型 - {building_name}"
        },
        "properties": {
            "floor_id": {"type": "STRING"},
            "floor_name": {"type": "STRING"},
            "floor_type": {"type": "STRING"},
            "building_id": {"type": "STRING"},
        },
        "geometricError": 1.0,
        "root": {
            "boundingVolume": {
                "box": [60, 12, 45, 60, 24, 45]
            },
            "geometricError": 0.5,
            "refine": "ADD",
            "content": {
                "uri": f"{building_id}_L1.gltf",
                "boundingVolume": {"box": [60, 8, 45, 60, 8, 45]}
            },
            "children": []
        }
    }
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(tileset, f, indent=2, ensure_ascii=False)


print("=" * 50)
print("GeoHUB 3D 模型生成器")
print("=" * 50)

# 生成每层 glTF
for floor in FLOORS:
    print(f"  生成楼层: {floor['name']}")
    
    # 创建楼层场景
    scene = trimesh.Scene()
    
    # 楼板
    floor_slab = trimesh.creation.box(
        extents=[120, 0.4, 90],
        transform=trimesh.transformations.translation_matrix([60, floor["y"] - 0.2, 45])
    )
    
    # 地板网格
    grid_verts = []
    grid_idx = []
    for xi in range(0, 121, 10):
        grid_verts.extend([[xi, floor["y"], 0], [xi, floor["y"], 90]])
        grid_idx.extend([len(grid_verts)-2, len(grid_verts)-1])
    for zi in range(0, 91, 10):
        grid_verts.extend([[0, floor["y"], zi], [120, floor["y"], zi]])
        grid_idx.extend([len(grid_verts)-2, len(grid_verts)-1])
    
    grid_v = np.array(grid_verts)
    grid_mesh = trimesh.Trimesh(vertices=grid_v, faces=np.array(grid_idx).reshape(-1,2) if len(grid_idx)>2 else np.zeros((0,3),dtype=np.uint32))
    
    all_meshes = [floor_slab]
    
    # 功能区
    type_colors_rgb = {
        "shop": [0.15, 0.40, 0.80],
        "dining": [0.85, 0.50, 0.10],
        "elevator": [0.70, 0.15, 0.90],
        "entrance": [0.15, 0.80, 0.40],
        "exit": [0.90, 0.15, 0.15],
        "toilet": [0.15, 0.60, 0.70],
    }
    
    for feat in floor.get("features", []):
        col = type_colors_rgb.get(feat["type"], [0.3, 0.3, 0.35])
        h = 0.5 if feat["type"] == "shop" else 0.3
        box = trimesh.creation.box(
            extents=[feat["w"], h, feat["d"]],
            transform=trimesh.transformations.translation_matrix([
                feat["x"] + feat["w"]/2,
                floor["y"] + h/2,
                feat["z"] + feat["d"]/2
            ])
        )
        box.visual.vertex_colors = [
            int(c * 255) for c in col + [0.85]
        ] * len(box.visual.vertex_colors)
        all_meshes.append(box)
    
    combined = trimesh.util.concatenate(all_meshes)
    
    metadata = {
        "geohub_metadata": {
            "floor_id": floor["id"],
            "floor_name": floor["name"],
            "floor_type": floor["type"],
            "building_id": "B000A856LJ",
            "building_name": "北京国贸中心",
            "floor_y_meters": floor["y"],
            "generated": "2026-07-29",
            "coordinate_system": "indoor_local",
            "origin_lnglat": [116.4603, 39.9093],
            "scale": {"x_meters_per_lng": 60000, "z_meters_per_lat": 90000}
        }
    }
    
    out_file = OUT / f"{floor['id']}_geohub.gltf"
    make_glTF(combined, out_file, floor["name"], metadata)
    size_kb = out_file.stat().st_size // 1024
    print(f"    ✅ {out_file.name} ({size_kb} KB)")


# 生成 Tileset JSON
ts_path = OUT / "guomao_tileset.json"
generate_3dtileset_json(ts_path, "北京国贸中心", "B000A856LJ")
print(f"\n  ✅ Tileset: {ts_path.name}")


# 生成汇总 README
readme = f"""# GeoHUB 3D 模型包 - 北京国贸中心

生成时间: 2026-07-29
模型格式: glTF 2.0 (.gltf)
坐标系: 室内局部坐标系 (原点: 116.4603°E, 39.9093°N)

## 上传到 GeoHUB

### 方法一：逐层上传（推荐）

1. 打开 https://geohub.amap.com → 登录
2. 点击「数据中心」→「上传数据」
3. 选择文件类型：3D模型
4. 逐个上传以下 .gltf 文件：

{FLOOR_LIST}

5. 上传完成后，在「我的数据」中获取每个文件的 API 地址

### 方法二：GeoJSON 批量上传（用于 POI 标注）

上传 `国贸中心_geojson.geojson` 到 GeoHUB Data Hub，
用于楼层 POI 标注（店铺、设施等）

## 坐标系说明

- 室内坐标转经纬度：
  lng = indoor_x / 60000 + 116.4603
  lat = indoor_z / 90000 + 39.9093
- 楼层高度（Y轴，米）：
{FLOOR_Y}

## 文件清单

| 文件 | 描述 | 大小 |
|------|------|------|
"""

floor_list_lines = []
floor_y_lines = []
total_size = 0
for floor in FLOORS:
    f = OUT / f"{floor['id']}_geohub.gltf"
    if f.exists():
        sz = f.stat().st_size
        total_size += sz
        floor_list_lines.append(f"| {f.name} | {floor['name']} | {sz//1024} KB |")
    floor_y_lines.append(f"| {floor['id']} | {floor['y']}m | {floor['type']} |")

readme += "\n".join(floor_list_lines)
readme += f"\n| **总计** | | **{total_size//1024} KB** |\n\n## 楼层高度\n\n| 楼层 | Y轴高度 | 类型 |\n|------|---------|------|\n"
readme += "\n".join(floor_y_lines)
readme += """

## 接入代码（indoor_map_final.html 中）

```javascript
// GeoHUB 3D Tiles 接入
const tileset = new AMap.3DTileset({
    url: 'https://restapi.geohub.amap.com/v1/3dtiles/你的TilesetID/tileset.json',
    position: new AMap.LngLat(116.4608, 39.9097),
    height: 0,
    scene: mapObj.getMap()
});
tileset.setMap(mapObj);
tileset.on('click', e => { /* 点击楼层模型 */ });
```

"""
with open(OUT / "README.md", 'w', encoding='utf-8') as f:
    f.write(readme)

print(f"\n  ✅ README: README.md")
print(f"\n总计: {len(FLOORS)} 层模型, {total_size//1024} KB")
print("  所有文件已保存到:", OUT)
