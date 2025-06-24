import bpy

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

# Set frame range
start = int(bpy.context.scene.frame_start)
end = int(bpy.context.scene.frame_end)

bpy.ops.pose.select_all(action='SELECT')
bpy.ops.nla.bake(frame_start=start,
                 frame_end=end,
                 only_selected=True,
                 visual_keying=True,
                 clear_constraints=True,
                 use_current_action=True,
                 bake_types={'POSE'})