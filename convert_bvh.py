import bpy
import numpy as np
import mathutils

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

bones = armature.pose.bones
bone_names = [b.name for b in bones]

for bone in bones:
    dof_names.append(bone.name)
    body_names.append(bone.name)

for f in range(frame_start, frame_end + 1):
    scene.frame_set(f)
    bpy.context.scene.update()

    frame_dof_pos = []
    frame_body_pos = []
    frame_body_rot = []

    for bone in bones:
        pos = bone.head.copy()
        rot = bone.matrix.to_quaternion()

        frame_dof_pos.append(pos.x)  # could be extended for more DOFs
        frame_body_pos.append([pos.x, pos.y, pos.z])
        frame_body_rot.append([rot.w, rot.x, rot.y, rot.z])  # wxyz format

    dof_positions.append(frame_dof_pos)
    body_positions.append(frame_body_pos)
    body_rotations.append(frame_body_rot)

    # Compute velocities if not first frame
    if last_frame_positions is not None:
        frame_dof_vel = []
        frame_body_vel = []
        frame_body_ang_vel = []

        for i in range(len(bones)):
            pos_now = mathutils.Vector(body_positions[-1][i])
            pos_prev = mathutils.Vector(last_frame_positions[i])
            vel = (pos_now - pos_prev) / dt
            frame_body_vel.append([vel.x, vel.y, vel.z])

            rot_now = mathutils.Quaternion(body_rotations[-1][i])
            rot_prev = mathutils.Quaternion(last_frame_rotations[i])
            delta_rot = rot_now * rot_prev.conjugated()
            axis, angle = delta_rot.axis, delta_rot.angle
            ang_vel = (angle / dt) * axis
            frame_body_ang_vel.append([ang_vel.x, ang_vel.y, ang_vel.z])

            # For DOF velocity, let's just use root bone's x position diff for now
            frame_dof_vel.append((frame_dof_pos[i] - last_frame_dof[i]) / dt)

        dof_velocities.append(frame_dof_vel)
        body_linear_velocities.append(frame_body_vel)
        body_angular_velocities.append(frame_body_ang_vel)
    else:
        # For first frame, just fill zeros
        dof_velocities.append([[0.0] * len(bones)][0])
        body_linear_velocities.append([[0.0, 0.0, 0.0]] * len(bones))
        body_angular_velocities.append([[0.0, 0.0, 0.0]] * len(bones))

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

# Save to file (adjust path for Windows)
output_path = bpy.path.abspath("//humanoid_motion.npz")
np.savez(output_path, **npz_data)

print("Saved motion to", output_path)