#!/bin/bash
#/home/lab/workspace/sean/blender-2.79b-linux-glibc219-x86_64/blender
#find ../Data/momask_bvh_files/ -type f -path "*/animations/0/*.bvh" ! -name "*_ik.bvh" -exec blender -b -P bvh_to_fbx.py -- {} \;
find ../Data/momask_bvh_files/ -type f -path "*/animations/0/*.bvh" ! -name "*_ik.bvh" -exec /home/lab/workspace/sean/blender-2.79b-linux-glibc219-x86_64/blender -b -P bvh_to_fbx.py -- {} \;