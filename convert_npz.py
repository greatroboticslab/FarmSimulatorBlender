import bpy
import numpy as np
import mathutils
import os

# Change this to match your armature name
armature = bpy.data.objects["Skeleton"]
scene = bpy.context.scene

fps = scene.render.fps
dt = 1.0 / fps
frame_start = scene.frame_start
frame_end = scene.frame_end
num_frames = frame_end - frame_start + 1

bpy.context.scene.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# Assuming 1 bone per DOF/body for simplicity
dof_names = []
body_names = []
dof_positions = []
dof_velocities = []
body_positions = []
body_rotations = []
body_linear_velocities = []
body_angular_velocities = []

last_frame_positions = None
last_frame_rotations = None

# Convert Unity skeleton to AMP skeleton. Returns "NULL" if a bone is discarded
def ConvertBoneName(boneName):
    
    if(boneName == "Hips"):
        return "pelvis"
    if(boneName == "Chest"):
        return "torso"
    if(boneName == "Head"):
        return "head"
        
    if(boneName == "Right_UpperArm"):
        return "right_upper_arm"
    if(boneName == "Right_LowerArm"):
        return "right_lower_arm"
    if(boneName == "Right_Hand"):
        return "right_hand"
        
    if(boneName == "Left_UpperArm"):
        return "left_upper_arm"
    if(boneName == "Left_LowerArm"):
        return "left_lower_arm"
    if(boneName == "Left_Hand"):
        return "left_hand"
    
    if(boneName == "Right_UpperLeg"):
        return "right_thigh"
    if(boneName == "Right_LowerLeg"):
        return "right_shin"
    if(boneName == "Right_Foot"):
        return "right_foot"
    
    if(boneName == "Left_UpperLeg"):
        return "left_thigh"
    if(boneName == "Left_LowerLeg"):
        return "left_shin"
    if(boneName == "Left_Foot"):
        return "left_foot"
    
    return "NULL"
    
    
# G1 naming convention
def ConvertBoneNameG1(boneName):
    
    if(boneName == "Hips"):
        return "pelvis"
        
    if(boneName == "Right_UpperArm"):
        return "right_shoulder_pitch_link"
    if(boneName == "Right_LowerArm"):
        return "right_elbow_link"
    if(boneName == "Right_Hand"):
        return "right_rubber_hand"
        
    if(boneName == "Left_UpperArm"):
        return "left_shoulder_pitch_link"
    if(boneName == "Left_LowerArm"):
        return "left_elbow_link"
    if(boneName == "Left_Hand"):
        return "left_rubber_hand"
    
    if(boneName == "Right_UpperLeg"):
        return "right_hip_yaw_link"
    if(boneName == "Right_Foot"):
        return "right_ankle_roll_link"
    
    if(boneName == "Left_UpperLeg"):
        return "left_hip_yaw_link"
    if(boneName == "Left_Foot"):
        return "left_ankle_roll_link"
    
    return "NULL"

#What type of name is appended to a joint string, errors have occured using joint_name_xyz instead of pitch yaw roll
def JointNameConvention(xyz, convention):
    if xyz == 1:
        if convention == 1:
            return "_x"
        if convention == 2:
            return "_pitch_joint"
    if xyz == 2:
        if convention == 1:
            return "_y"
        if convention == 2:
            return "_yaw_joint"
    if xyz == 3:
        if convention == 1:
            return "_z"
        if convention == 2:
            return "_roll_joint"
    return ""
    
def ConvertToDOF(b):
    
    names = []
    bones = []
    output = []
    
    n = ConvertBoneName(b.name)
    
    if n == "pelvis":
        names.append("waist" + JointNameConvention(1,2))
        names.append("waist" + JointNameConvention(2,2))
        names.append("waist" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    
    if n == "torso":
        names.append("abdomen" + JointNameConvention(1,2))
        names.append("abdomen" + JointNameConvention(2,2))
        names.append("abdomen" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "head":
        names.append("neck" + JointNameConvention(1,2))
        names.append("neck" + JointNameConvention(2,2))
        names.append("neck" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "right_upper_arm":
        names.append("right_shoulder" + JointNameConvention(1,2))
        names.append("right_shoulder" + JointNameConvention(2,2))
        names.append("right_shoulder" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "right_lower_arm":
        names.append("right_elbow_joint")
        bones.append(b)
        
    if n == "left_upper_arm":
        names.append("left_shoulder" + JointNameConvention(1,2))
        names.append("left_shoulder" + JointNameConvention(2,2))
        names.append("left_shoulder" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "left_lower_arm":
        names.append("left_elbow_joint")
        bones.append(b)
        
    
    if n == "right_thigh":
        names.append("right_hip" + JointNameConvention(1,2))
        names.append("right_hip" + JointNameConvention(2,2))
        names.append("right_hip" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "right_shin":
        names.append("right_knee_joint")
        bones.append(b)
        
    if n == "right_foot":
        names.append("right_ankle" + JointNameConvention(1,2))
        names.append("right_ankle" + JointNameConvention(2,2))
        names.append("right_ankle" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "left_thigh":
        names.append("left_hip" + JointNameConvention(1,2))
        names.append("left_hip" + JointNameConvention(2,2))
        names.append("left_hip" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "left_shin":
        names.append("left_knee_joint")
        bones.append(b)
        
    if n == "left_foot":
        names.append("left_ankle" + JointNameConvention(1,2))
        names.append("left_ankle" + JointNameConvention(2,2))
        names.append("left_ankle" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    if n == "left_hand":
        names.append("left_wrist" + JointNameConvention(1,2))
        names.append("left_wrist" + JointNameConvention(2,2))
        names.append("left_wrist" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
    
    if n == "right_hand":
        names.append("right_wrist" + JointNameConvention(1,2))
        names.append("right_wrist" + JointNameConvention(2,2))
        names.append("right_wrist" + JointNameConvention(3,2))
        bones.append(b)
        bones.append(b)
        bones.append(b)
        
    output = [names, bones]
        
    return output
        

#All bones, before conversion

pre_bones = armature.pose.bones

bones = []
g1_bones = []

for b in pre_bones:
    if ConvertBoneName(b.name) != "NULL":
        bones.append(b)
    if ConvertBoneNameG1(b.name) != "NULL":
        g1_bones.append(b)

for bone in pre_bones:
    #dof_names.append(bone.name)
    subDOFs = ConvertToDOF(bone)
    for i in range(len(subDOFs[0])):
        print(subDOFs[0][i])
        dof_names.append(subDOFs[0][i])
        
    if ConvertBoneNameG1(bone.name) != "NULL":
        body_names.append(ConvertBoneNameG1(bone.name))

for f in range(frame_start, frame_end + 1):
    scene.frame_set(f)
    bpy.context.scene.update()

    frame_dof_pos = []
    frame_body_pos = []
    frame_body_rot = []

    for bone in pre_bones:
        
        
        #ConvertToDOF(bone)
        
        subDOFs = ConvertToDOF(bone)
        for i in range(len(subDOFs[0])):
            dpos = subDOFs[1][i].head.copy()
            frame_dof_pos.append(dpos.x)
        
        if ConvertBoneNameG1(bone.name) != "NULL":
            pos = bone.head.copy()
            rot = bone.matrix.to_quaternion()
            #frame_dof_pos.append(pos.x)  # could be extended for more DOFs
            frame_body_pos.append([pos.z, pos.x, pos.y])
            frame_body_rot.append([rot.w, rot.x, rot.y, rot.z])  # wxyz format

    dof_positions.append(frame_dof_pos)
    body_positions.append(frame_body_pos)
    body_rotations.append(frame_body_rot)

    # Compute velocities if not first frame
    if last_frame_positions is not None:
        frame_dof_vel = []
        frame_body_vel = []
        frame_body_ang_vel = []

        j = 0

        for i in range(len(g1_bones)):
        
            if ConvertBoneNameG1(g1_bones[i].name) != "NULL":
        
                pos_now = mathutils.Vector(body_positions[-1][i])
                pos_prev = mathutils.Vector(last_frame_positions[i])
                vel = (pos_now - pos_prev) / dt
                
                #Change XYZ to ZXY to fit AMP convention for IsaacLab
                
                frame_body_vel.append([vel.z, vel.x, vel.y])

                rot_now = mathutils.Quaternion(body_rotations[-1][i])
                rot_prev = mathutils.Quaternion(last_frame_rotations[i])
                delta_rot = rot_now * rot_prev.conjugated()
                axis, angle = delta_rot.axis, delta_rot.angle
                ang_vel = (angle / dt) * axis
                frame_body_ang_vel.append([ang_vel.z, ang_vel.x, ang_vel.y])

            # For DOF velocity, let's just use root bone's x position diff for now
            subDOFs = ConvertToDOF(g1_bones[i])
            for k in range(len(subDOFs[0])):
                frame_dof_vel.append(frame_dof_pos[i] - last_frame_dof[i] / dt)
                j += 1
            #frame_dof_vel.append((frame_dof_pos[i] - last_frame_dof[i]) / dt)

        #dof_velocities.append(frame_dof_vel)
        body_linear_velocities.append(frame_body_vel)
        body_angular_velocities.append(frame_body_ang_vel)
    else:
        # For first frame, just fill zeros
        dof_velocities.append([[0.0] * len(dof_positions)][0])
        #dof_velocities.append([[0.0] * len(bones)][0])
        
        
        body_linear_velocities.append([[0.0, 0.0, 0.0]] * len(g1_bones))
        body_angular_velocities.append([[0.0, 0.0, 0.0]] * len(g1_bones))

    last_frame_positions = body_positions[-1]
    last_frame_rotations = body_rotations[-1]
    last_frame_dof = frame_dof_pos

# Convert everything to NumPy
npz_data = {
    "fps": fps,
    "dof_names": np.array(dof_names),
    "body_names": np.array(body_names),
    "dof_positions": np.array(dof_positions).astype(np.float32),
    "dof_velocities": np.array(dof_velocities).astype(np.float32),
    "body_positions": np.array(body_positions).astype(np.float32),
    "body_rotations": np.array(body_rotations).astype(np.float32),
    "body_linear_velocities": np.array(body_linear_velocities).astype(np.float32),
    "body_angular_velocities": np.array(body_angular_velocities).astype(np.float32),
}


blend_filepath = bpy.data.filepath
blend_filename = os.path.basename(blend_filepath)
project_name = os.path.splitext(blend_filename)[0]

output_path = bpy.path.abspath("//"+project_name+".npz")
np.savez(output_path, **npz_data)

print("Saved motion to", output_path)