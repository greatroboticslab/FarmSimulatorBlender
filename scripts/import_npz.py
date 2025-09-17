import bpy
import numpy as np
import os

# Load the NPZ file
npz_path = bpy.path.abspath("//humanoid_animation_harvest1.npz")
data = np.load(npz_path)

fps = int(data["fps"])
dof_names = data["dof_names"]
dof_positions = data["dof_positions"]

scene = bpy.context.scene
scene.render.fps = fps
frame_start = scene.frame_start
frame_end = frame_start + len(dof_positions) - 1
scene.frame_end = frame_end

# Your armature object
armature = bpy.data.objects["Skeleton"]
bpy.context.scene.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# Create a mapping from DOF names to bones
# You might need to refine this map based on your rig
def dof_to_bone_map(dof_name):
    # e.g. 'right_shoulder_pitch_joint' -> ('Right_UpperArm', 'X')
    if "right_shoulder" in dof_name:
        return ("Right_UpperArm", 'rotation')
    if "left_shoulder" in dof_name:
        return ("Left_UpperArm", 'rotation')
    if "right_elbow" in dof_name:
        return ("Right_LowerArm", 'rotation')
    if "left_elbow" in dof_name:
        return ("Left_LowerArm", 'rotation')
    if "right_hip" in dof_name:
        return ("Right_UpperLeg", 'rotation')
    if "left_hip" in dof_name:
        return ("Left_UpperLeg", 'rotation')
    if "right_knee" in dof_name:
        return ("Right_LowerLeg", 'rotation')
    if "left_knee" in dof_name:
        return ("Left_LowerLeg", 'rotation')
    if "waist" in dof_name:
        return ("Hips", 'rotation')
    return (None, None)

# Apply animation
for frame_idx, pose_frame in enumerate(dof_positions):
    scene.frame_set(frame_start + frame_idx)
    
    for i, dof_value in enumerate(pose_frame):
        dof_name = str(dof_names[i])
        bone_name, channel_type = dof_to_bone_map(dof_name)

        if bone_name is None or bone_name not in armature.pose.bones:
            continue

        bone = armature.pose.bones[bone_name]

        if channel_type == 'rotation':
            if not hasattr(bone, 'rotation_euler'):
                continue
            bone.rotation_mode = 'XYZ'
            axis_index = ['_pitch', '_yaw', '_roll']
            axis = next((j for j, a in enumerate(axis_index) if a in dof_name), None)
            if axis is not None:
                bone.rotation_euler[axis] = dof_value
                bone.keyframe_insert(data_path="rotation_euler", frame=frame_start + frame_idx, index=axis)

print("Animation applied from NPZ.")
