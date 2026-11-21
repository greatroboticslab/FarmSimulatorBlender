[Back to the main page](../README.md)

# Preparing a scanned (VGGT) model in Blender 

In the following, I will show you how to do aapple assests making using the blender and once finished, it can be expored to Unity 

## VGGT Post-Processing and Export

Remeshed VGGT pointclouds need to be processed in Blender before they can be exported to Unity.

![vggt1](../Media/bl1.png "Step 1")

1. Import the remeshed pointcloud .obj (processed by MeshLab) into Blender.

![vggt2](../Media/bl2.png "Step 2")

2. It should look like this. Press TAB to go into edit mode.

![vggt3](../Media/bl3.png "Step 3")

3. Rotate the mesh 180 degrees along the Y axis.

![vggt4](../Media/bl4.png "Step 4")

4.  Move the center of the fruit/plant to be located at the origin. This typically only involves moving the mesh in the direction of the green arrow.

![vggt5](../Media/bl5.png "Step 5")

5. Rotate the mesh along the Z axis 180 degrees, so that the back of the mesh is pointing the same direction as the green arrow.

![vggt6](../Media/bl6.png "Step 6")

6. Split the view into the 3D viewer and the UV image editor. Then press numpad 1 to view the model from the front. Zoom in and hold shift + middle mouse button to move the view until the front of the mesh is roughly square shaped.

![vggt7](../Media/bl7.png "Step 7")

7. Exit edit mode, and create a new material in the materials tab.

![vggt8](../Media/bl8.png "Step 8")

8. Once a new material is created, go to the texture tab and create a new texture.

![vggt9](../Media/bl9.png "Step 9")

9. After making the new texture, click the open button, and selected the mesh's texture, typically located in the Data/vggt_images/ folder.

![vggt10](../Media/bl10.png "Step 10")

10. Open the image preview in the UV image editor.

![vggt11](../Media/bl11.png "Step 11")

11. Select the mesh, go into edit mode, and select all the vertices. Then press U, and choose Project from View (Bounds).

![vggt12](../Media/bl12.png "Step 12")

12. The UV layout should be roughly square shaped in the UV Image Editor. scale and move the UVs to match the mesh. You can go into Texture preview mode to preview the mesh and its texture in the 3D view.

![vggt13](../Media/bl13.png "Step 13")

13. While in edit mode, select faces of the mesh that should be deleted (background). Select face mode, and press C to use the circle select tool to more easily select them.

![vggt14](../Media/bl14.png "Step 14")

14. Delete these faces, and exit edit mode.

![vggt15](../Media/bl15.png "Step 15")

15. Export the mesh as an .obj to the output/ folder.
