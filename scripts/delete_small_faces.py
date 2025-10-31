import bpy
import bmesh

# Get the active mesh
obj = bpy.context.object
me = obj.data

# Make sure we're in Edit Mode and using BMesh
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(me)

# Define minimum area threshold
min_area = 0.0001  # adjust as needed

# Find and remove faces below threshold
faces_to_delete = [f for f in bm.faces if f.calc_area() < min_area]
bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')

# Update mesh
bmesh.update_edit_mesh(me)
print(f"Deleted {len(faces_to_delete)} small faces.")