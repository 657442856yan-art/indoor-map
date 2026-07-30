import sys, json, struct, base64, os
from pathlib import Path

sys.path.insert(0, r'C:\Users\严梓轩\AppData\Roaming\Python\Python311\Lib\site-packages')
import numpy as np
import trimesh

OUT = Path(r'C:\Users\严梓轩\.openclaw\workspace\geohub_data')
OUT.mkdir(exist_ok=True)

FLOORS = [
    {'id':'B2','name':'B2-Parking','y':0,'type':'parking','features':[]},
    {'id':'B1','name':'B1-Supermarket','y':4,'type':'shopping','features':[{'x':36,'z':27,'w':28,'d':20,'type':'shop','name':'Ole'},{'x':72,'z':18,'w':18,'d':14,'type':'shop','name':'Starbucks'}]},
    {'id':'L1','name':'L1-Luxury','y':8,'type':'shopping','features':[{'x':20,'z':40,'w':18,'d':16,'type':'shop','name':'Chanel'},{'x':60,'z':45,'w':18,'d':14,'type':'shop','name':'Dior'},{'x':95,'z':30,'w':16,'d':12,'type':'elevator','name':'ElevA'}]},
    {'id':'L2','name':'L2-Fashion','y':12,'type':'shopping','features':[{'x':22,'z':35,'w':22,'d':18,'type':'shop','name':'Gucci'},{'x':60,'z':40,'w':20,'d':16,'type':'shop','name':'Prada'}]},
    {'id':'L3','name':'L3-Trendy','y':16,'type':'shopping','features':[{'x':18,'z':36,'w':20,'d':16,'type':'shop','name':'ZARA'},{'x':55,'z':42,'w':20,'d':16,'type':'shop','name':'UNIQLO'},{'x':88,'z':36,'w':18,'d':14,'type':'shop','name':'Nike'}]},
    {'id':'L4','name':'L4-Dining','y':20,'type':'dining','features':[{'x':20,'z':36,'w':24,'d':20,'type':'shop','name':'LvCha'},{'x':60,'z':30,'w':20,'d':16,'type':'shop','name':'Waipojia'},{'x':90,'z':42,'w':16,'d':14,'type':'shop','name':'DTF'}]},
    {'id':'L5','name':'L5-Entertainment','y':24,'type':'entertainment','features':[]},
]

TCOLS = {'shop':[0.15,0.40,0.80],'dining':[0.85,0.50,0.10],'elevator':[0.70,0.15,0.90],
         'entrance':[0.15,0.80,0.40],'exit':[0.90,0.15,0.15],'toilet':[0.15,0.60,0.70]}

all_v,all_n,all_c,all_i = [],[],[],[]
base = 0
total_verts = 0
total_faces = 0

for fl in FLOORS:
    meshes = []
    slab = trimesh.creation.box([120,0.4,90],
        transform=trimesh.transformations.translation_matrix([60,fl['y']-0.2,45]))
    slab.visual.vertex_colors = [[int(c*255) for c in [0.12,0.15,0.22,220]]]*len(slab.vertices)
    meshes.append(slab)
    for feat in fl.get('features',[]):
        col = TCOLS.get(feat['type'],[0.3,0.3,0.35])
        box = trimesh.creation.box([feat['w'],0.5,feat['d']],
            transform=trimesh.transformations.translation_matrix([feat['x']+feat['w']/2,fl['y']+0.25,feat['z']+feat['d']/2]))
        box.visual.vertex_colors = [[int(c*255) for c in col+[210]]]*len(box.vertices)
        meshes.append(box)
    combined = trimesh.util.concatenate(meshes)

    face_n = np.zeros_like(combined.vertices)
    for fi in combined.faces:
        v0,v1,v2 = combined.vertices[fi[0]],combined.vertices[fi[1]],combined.vertices[fi[2]]
        n = np.cross(v1-v0, v2-v0)
        nl = np.linalg.norm(n)
        if nl > 1e-10: n = n/nl
        for vi in fi: face_n[vi] += n
    norms = np.zeros_like(face_n)
    for i in range(len(norms)):
        nl = np.linalg.norm(face_n[i])
        if nl > 1e-10: norms[i] = face_n[i]/nl

    all_v.extend(combined.vertices.flatten().tolist())
    all_n.extend(norms.flatten().tolist())
    c = TCOLS.get(fl['type'],[0.3,0.3,0.35])
    all_c.extend(([c[0],c[1],c[2],0.9]*len(combined.vertices)))
    for idx in combined.faces:
        all_i.extend([idx[0]+base,idx[1]+base,idx[2]+base])
    base += len(combined.vertices)
    total_verts += len(combined.vertices)
    total_faces += len(combined.faces)
    print(f'[{fl["id"]}] verts={len(combined.vertices)}, faces={len(combined.faces)}')

vc = len(all_v)//3
ic = len(all_i)
vb = struct.pack('<%df' % len(all_v), *all_v)
nb = struct.pack('<%df' % len(all_n), *all_n)
cb = struct.pack('<%df' % len(all_c), *all_c)
ib = struct.pack('<%dI' % len(all_i), *all_i)
b64_data = base64.b64encode(vb+nb+cb+ib).decode()
total_bytes = len(vb)+len(nb)+len(cb)+len(ib)

gltf = {
    'asset':{'version':'2.0','generator':'GeoHUB-Model-Gen-v1 (QClaw)'},
    'scene':0,'scenes':[{'nodes':[0]}],
    'nodes':[{'mesh':0,'name':'GuomaoIndoorAllFloors'}],
    'meshes':[{
        'name':'GuomaoIndoorComplete',
        'primitives':[{
            'attributes':{'POSITION':0,'NORMAL':1,'COLOR_0':2},
            'indices':3,
            'material':0,
            'mode':4
        }]
    }],
    'accessors':[
        {'bufferView':0,'componentType':5126,'count':vc,'type':'VEC3','max':[120,27,90],'min':[0,0,0]},
        {'bufferView':1,'componentType':5126,'count':vc,'type':'VEC3'},
        {'bufferView':2,'componentType':5126,'count':vc,'type':'VEC4'},
        {'bufferView':3,'componentType':5125,'count':ic,'type':'SCALAR'}
    ],
    'bufferViews':[
        {'buffer':0,'byteOffset':0,'byteLength':len(vb),'target':34962},
        {'buffer':0,'byteOffset':len(vb),'byteLength':len(nb),'target':34962},
        {'buffer':0,'byteOffset':len(vb)+len(nb),'byteLength':len(cb),'target':34962},
        {'buffer':0,'byteOffset':len(vb)+len(nb)+len(cb),'byteLength':len(ib),'target':34963}
    ],
    'buffers':[{'byteLength':total_bytes,'uri':'data:model/gltf;base64,'+b64_data}],
    'materials':[{
        'name':'indoor_mat',
        'pbrMetallicRoughness':{'baseColorFactor':[0.8,0.8,0.85,0.9],'metallicFactor':0.1,'roughnessFactor':0.7},
        'alphaMode':'BLEND',
        'doubleSided':True
    }],
    'extras':{
        'geohub_indoor':{
            'building_id':'B000A856LJ',
            'building_name':'Guomao Center Beijing',
            'floors':[{'id':f['id'],'y_meters':f['y'],'type':f['type']} for f in FLOORS],
            'coordinate_origin':{'lng':116.4603,'lat':39.9093},
            'scale':{'x_meters_per_lng':60000,'z_meters_per_lat':90000}
        }
    }
}

out_all = OUT / 'guomao_indoor_all.gltf'
with open(out_all, 'w', encoding='utf-8') as f:
    json.dump(gltf, f, indent=2)
sz = out_all.stat().st_size
print('Total verts=%d faces=%d Size=%d KB' % (total_verts, total_faces, sz//1024))
print('Output:', out_all)
print('DONE')
