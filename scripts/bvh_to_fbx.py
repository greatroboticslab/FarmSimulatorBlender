import bpy
import os
import sys
from pathlib import Path

# sys.argv includes Blender's own arguments, so we need to find the '--'
argv = sys.argv
if "--" in argv:
    args = argv[argv.index("--") + 1:]  # everything after '--'
else:
    args = []

bvh_path = args[0]


p = Path(bvh_path)
# Get all parts of the path
parts = p.parts
# Keep only the last 6 parents + the file itself
tPath = parts[-7:]

output_dir = Path(*tPath)
output_dir = "../Data/unity_fbx_files/" + str(output_dir)[:-4] + ".fbx"
#output_dir = "../Data/unity_fbx_files/" + os.path.basename(bvh_path)

if len(args) > 1:
    output_dir = args[1]

print(output_dir)

#quit()

if not os.path.exists(bvh_path):
    print("ERROR: BVH file not found:", bvh_path)
    sys.exit(1)

# Delete default scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


# --- Record current objects before import ---
before = set(bpy.data.objects.keys())

# --- Import BVH ---
bpy.ops.import_anim.bvh(filepath=bvh_path, axis_forward='-Z', axis_up='Y')

# --- Find what new objects appeared ---
after = set(bpy.data.objects.keys())
new_objects = after - before

if not new_objects:
    print("No new objects found after BVH import!")
    sys.exit(1)

# --- Assign imported armature to a variable ---
imported_obj_name = list(new_objects)[0]
bvh_obj = bpy.data.objects[imported_obj_name]


# Import FBX --------------------------------------------------------


before_fbx = set(bpy.data.objects.keys())
bpy.ops.import_scene.fbx(filepath="../Unity Armature.fbx")
after_fbx = set(bpy.data.objects.keys())
fbx_objects = after_fbx - before_fbx

if not fbx_objects:
    print("No FBX objects imported!")
    sys.exit(1)

# Usually FBX contains meshes and possibly an armature
fbx_objs = [bpy.data.objects[name] for name in fbx_objects]
print("Imported FBX objects:", [obj.name for obj in fbx_objs])

# If you want just the armature from FBX (if it has one):
fbx_armatures = [obj for obj in fbx_objs if obj.type == 'ARMATURE']
fbx_meshes = [obj for obj in fbx_objs if obj.type == 'MESH']

fbx_armature = fbx_armatures[0] if fbx_armatures else None

bvh_obj.select = True
fbx_armature.select = True

# Define bone mapping: target -> source
bone_map = {
    "Hips": "Hips",
    "Spine": "Spine",
    "Chest": "Spine1",
    "UpperChest": "Spine2",
    "Left_Shoulder": "LeftShoulder",
    "Left_UpperArm": "LeftArm",
    "Left_LowerArm": "LeftForeArm",
    "Left_Hand": "LeftHand",
    "Right_Shoulder": "RightShoulder",
    "Right_UpperArm": "RightArm",
    "Right_LowerArm": "RightForeArm",
    "Right_Hand": "RightHand",
    "Neck": "Neck",
    "Head": "Head",
    "Left_UpperLeg": "LeftUpLeg",
    "Left_LowerLeg": "LeftLeg",
    "Left_Foot": "LeftFoot",
    "Left_Toes": "LeftToe",
    "Right_UpperLeg": "RightUpLeg",
    "Right_LowerLeg": "RightLeg",
    "Right_Foot": "RightFoot",
    "Right_Toes": "RightToe"
}

# Validate selection
selected = bpy.context.selected_objects
if len(selected) < 2:
    raise Exception("Select the source armature first, then the target armature (active).")

target_arm = bpy.context.active_object
source_arm = [obj for obj in selected if obj != target_arm][0]

if target_arm.type != 'ARMATURE' or source_arm.type != 'ARMATURE':
    raise Exception("Both selected objects must be armatures.")

# Enter pose mode
bpy.context.scene.objects.active = target_arm
bpy.ops.object.mode_set(mode='POSE')

# Add constraints
for target_bone_name, source_bone_name in bone_map.items():
    try:
        pbone = target_arm.pose.bones[target_bone_name]
    except KeyError:
        print("Target bone not found:", target_bone_name)
        continue

    # Remove existing "Copy Rotation" constraints with the same name to avoid duplicates
    existing = [c for c in pbone.constraints if c.name == "CopyRotFrom_" + source_bone_name]
    for c in existing:
        pbone.constraints.remove(c)

    # Add new constraint
    constraint = pbone.constraints.new(type='COPY_ROTATION')
    constraint.name = "CopyRotFrom_" + source_bone_name
    constraint.target = source_arm
    constraint.subtarget = source_bone_name
    constraint.owner_space = 'LOCAL'
    constraint.target_space = 'LOCAL'

    print("Constraint added:", target_bone_name, "<-", source_bone_name)

print("✅ Copy Rotation constraints added.")

# Make sure we're working with the target (FBX) armature
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

bvh_obj.select = True

fbx_armature.select = True
bpy.context.scene.objects.active = fbx_armature

# Evaluate animation range based on source
start = bpy.context.scene.frame_start
end = bpy.context.scene.frame_end

print("Baking animation from frame {} to {}...".format(start, end))

# Enter pose mode and select all pose bones
# --- Bake animation ---
bpy.context.scene.objects.active = fbx_armature
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')

print("Baking animation from frame {} to {}...".format(start, end))

# Bake without clearing constraints yet
bpy.ops.nla.bake(
    frame_start=start,
    frame_end=end,
    only_selected=True,
    visual_keying=True,
    clear_constraints=False,  # important: keep constraints until after baking
    use_current_action=False,
    bake_types={'POSE'}
)

print("✅ Animation baked. Now assigning baked action...")


# Find the baked action (the most recent non-empty one)
baked_action = None
if fbx_armature.animation_data and fbx_armature.animation_data.action:
    baked_action = fbx_armature.animation_data.action
else:
    for action in bpy.data.actions:
        if len(action.fcurves) > 0:
            baked_action = action
            break

#if baked_action:
#    if not fbx_armature.animation_data:
#        fbx_armature.animation_data_create()
#    fbx_armature.animation_data.action = baked_action
#    print("Assigned baked action:", baked_action.name)
#else:
#    print("⚠️ No baked action found.")

# Now we can remove constraints safely
bpy.ops.object.mode_set(mode='POSE')
for bone in fbx_armature.pose.bones:
    for c in bone.constraints:
        bone.constraints.remove(c)
bpy.ops.object.mode_set(mode='OBJECT')

# --- Export to FBX ---
out_path = os.path.join(os.path.dirname(bpy.data.filepath), "processed_armature.fbx")

# Delete BVH
bpy.ops.object.select_all(action='DESELECT')
bvh_obj.select = True
bpy.ops.object.delete()



#baked_action = None
#for action in bpy.data.actions:
#    if len(action.fcurves) > 0:
#        baked_action = action
#        print("Found action:", action.name)

#if baked_action:
#    if not fbx_armature.animation_data:
#        fbx_armature.animation_data_create()
#    fbx_armature.animation_data.action = baked_action
#    print("Assigned baked action to FBX armature:", baked_action.name)
#else:
#    print("⚠️ No baked action found — export will have no animation.")


#bpy.ops.wm.save_as_mainfile(filepath=output_dir + ".blend")
#quit()

# output_path = os.path.join(os.getcwd(), "output_scene.blend")


bpy.ops.object.select_all(action='DESELECT')
fbx_armature.select = True
bpy.context.scene.objects.active = fbx_armature

#out_path = os.path.join(os.path.dirname(bpy.data.filepath), "processed_armature.fbx")
out_path = output_dir
os.makedirs(os.path.dirname(output_dir), exist_ok=True)
#bpy.ops.wm.save_as_mainfile(filepath=output_dir + ".blend")

bpy.ops.export_scene.fbx(
    filepath=out_path,
    use_selection=True,  # important: export only the active armature
    apply_unit_scale=True,
    global_scale=1.0,
    bake_space_transform=False,
    object_types={'ARMATURE', 'MESH'},
    use_mesh_modifiers=True,
    add_leaf_bones=False
)
print("✅ Exported FBX with animation:", out_path)