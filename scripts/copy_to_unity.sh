find ../Data/unity_fbx_files/ -type f -path "*/animations/0/*.fbx" ! -name "*_ik.bvh" \
-exec bash -c '
for src; do
    folder=$(basename "$(dirname "$(dirname "$(dirname "$src")")")")  # go up 3 levels
    dest="../../FarmSimulator/Assets/Resources/Animations/MoMask/${folder}.fbx"
    echo "Copying $src -> $dest"
    cp "$src" "$dest"
done
' bash {} +
