"""Task008-only Blender source/export helpers; never runs in Roblox."""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
# Reuse the project's original closed, indexed primitive builder.
sys.path.insert(0, str(ROOT / "assets/kolkata/howrah_bridge"))
from howrah_geometry import Geo, bp

PALETTE = {
    "Ivory": "E9E3D4", "Stone": "B3ACA0", "Charcoal": "343F45",
    "Brass": "B89B60", "Teal": "245D63", "Glass": "B6DADE",
    "Amber": "EDB554", "Oxblood": "88483F", "Paper": "E2D4AF",
    "Bronze": "99794D", "Sky": "8EB9BC", "River": "507D89",
    "Leaf": "4E7160", "Ink": "485260", "Gem": "3F8E89",
}

def material(role):
    key = "VIC008_" + role
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    h = PALETTE[role]
    srgb = [int(h[i:i+2], 16)/255 for i in (0,2,4)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in srgb]
    m = bpy.data.materials.new(key)
    if m.node_tree is None:m.use_nodes = True
    alpha = .10 if role == "Glass" else 1
    m.diffuse_color = (*linear, alpha)
    node = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = (*linear, 1)
    node.inputs["Alpha"].default_value = alpha
    node.inputs["Roughness"].default_value = .34 if role == "Glass" else .76
    node.inputs["Metallic"].default_value = .15 if role in ("Brass","Bronze") else 0
    if role == "Glass":
        m.surface_render_method = "BLENDED"  # Inspected in the connected Blender 5.2 RNA.
    return m

def triangles(mesh):
    return sum(len(p.vertices)-2 for p in mesh.polygons)

class Asset:
    def __init__(self, asset_id, category, name, cap, geo, *, pivot="Ground centre; front -Z", sockets=None, component_pivots=None, collision="Non-colliding visual; retain Task007 simple collision", note=""):
        self.id, self.category, self.name, self.cap = asset_id, category, name, cap
        self.sockets, self.note = sockets or {}, note
        self.scene = bpy.data.scenes.new(asset_id)
        bpy.context.window.scene = self.scene
        self.scene.unit_settings.system = "NONE"
        self.scene.unit_settings.scale_length = 1
        self.scene["AssetId"], self.scene["Task"] = asset_id, "008"
        self.collection = bpy.data.collections.new(asset_id)
        self.scene.collection.children.link(self.collection)
        self.objects = []
        for key, (vertices, faces) in geo.groups.items():
            component, role = key.split(":",1) if ":" in key else ("Body",key)
            origin = (component_pivots or {}).get(component, (0,0,0))
            mesh = bpy.data.meshes.new(asset_id+"__"+key.replace(":","__"))
            mesh.from_pydata([bp(tuple(p[i]-origin[i] for i in range(3))) for p in vertices], [], faces)
            mesh.update()
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            mesh.materials.append(material(role))
            if component == "Canvas":
                # One planar UV projection on the reusable physical backing.
                # Artwork itself is always a flat image, never sculpted geometry.
                uv=mesh.uv_layers.new(name="ArtworkUV")
                min_x=min(v.co.x for v in mesh.vertices);max_x=max(v.co.x for v in mesh.vertices)
                min_z=min(v.co.z for v in mesh.vertices);max_z=max(v.co.z for v in mesh.vertices)
                for loop in mesh.loops:
                    p=mesh.vertices[loop.vertex_index].co
                    uv.data[loop.index].uv=((p.x-min_x)/(max_x-min_x),(p.z-min_z)/(max_z-min_z))
            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.location = bp(origin)
            obj["AssetId"], obj["PaletteRole"], obj["Component"] = asset_id, role, component
            obj["CollisionRole"] = "Decoration"
            self.collection.objects.link(obj)
            self.objects.append(obj)
        self.scene.view_settings.view_transform = "Standard"
        self.folder = BASE / category / asset_id
        self.folder.mkdir(parents=True, exist_ok=True)
        points = [o.matrix_world @ v.co for o in self.objects for v in o.data.vertices]
        # Refresh matrices before calculating intentional component-pivot translations.
        bpy.context.view_layer.update()
        points = [o.matrix_world @ v.co for o in self.objects for v in o.data.vertices]
        low = [min(p[i] for p in points) for i in range(3)]
        high = [max(p[i] for p in points) for i in range(3)]
        total = sum(triangles(o.data) for o in self.objects)
        assert total <= cap, (asset_id,total,cap)
        self.row = dict(assetId=asset_id, category=category, name=name, triangles=total,
            triangleCap=cap, materialMeshes=len(self.objects), pivot=pivot,
            dimensionsStuds=dict(width=round(high[0]-low[0],4),height=round(high[2]-low[2],4),depth=round(high[1]-low[1],4)),
            boundsMinStuds=[round(low[0],5),round(low[2],5),round(-high[1],5)],
            boundsMaxStuds=[round(high[0],5),round(high[2],5),round(-low[1],5)],
            source=f"{category}/{asset_id}/{asset_id}.blend", export=f"{category}/{asset_id}/{asset_id}_Roblox.fbx",
            preview=f"{category}/{asset_id}/preview.png", materials=sorted({o["PaletteRole"] for o in self.objects}),
            sockets=self.sockets, componentPivots=component_pivots or {}, collision=collision, note=note,
            components=[dict(name=o.name,component=o["Component"],material=o["PaletteRole"],translationStuds=[o.location.x,o.location.z,-o.location.y],triangles=triangles(o.data)) for o in self.objects],
            textures=[], geometrySource="Original project geometry; authored for Task008")

    def save(self):
        for name, pos in {"MountOrigin":(0,0,0), **self.sockets}.items():
            empty = bpy.data.objects.new(self.id+"__"+name,None)
            empty.location = bp(pos)
            empty.empty_display_size = .25
            self.collection.objects.link(empty)
        bpy.data.libraries.write(str(BASE/self.row["source"]), {self.scene}, fake_user=True, compress=True)
        for o in self.scene.objects:
            o.select_set(False)
        for o in self.objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active = self.objects[0]
        bpy.ops.export_scene.fbx(filepath=str(BASE/self.row["export"]),use_selection=True,
            object_types={"MESH"},global_scale=1,apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="-Z",axis_up="Y",use_mesh_modifiers=False,bake_anim=False,
            path_mode="AUTO",mesh_smooth_type="FACE",use_custom_props=True,use_triangles=False)
        (self.folder/"asset.json").write_text(json.dumps(self.row,indent=2)+"\n")
        print(f"SAVED {self.id}: {self.row['triangles']}/{self.cap} triangles",flush=True)
        return self.row

def save_library(assets):
    scene = bpy.data.scenes.new("VIC_Interior_Library")
    bpy.context.window.scene = scene
    scene.unit_settings.system = "NONE"
    scene.unit_settings.scale_length = 1
    scene["Task"], scene["Instructions"] = "008", "Asset-sized scenes export at origin. This overview uses linked collection instances only."
    for ci, category in enumerate(("Architecture","Exhibition","Loot","Security")):
        collection = bpy.data.collections.new(category)
        scene.collection.children.link(collection)
        for index, asset in enumerate(a for a in assets if a.category == category):
            instance = bpy.data.objects.new(asset.id,None)
            instance.instance_type = "COLLECTION"
            instance.instance_collection = asset.collection
            instance.location = (index%5*15, -(ci*42+index//5*18), 0)
            collection.objects.link(instance)
    # Write only deliberate Task008 scenes. Leave the user's open Blender untouched.
    scenes = {a.scene for a in assets} | {scene}
    bpy.data.libraries.write(str(BASE/"VIC_Interior_Library.blend"),scenes,fake_user=True,compress=True)
    return scene
