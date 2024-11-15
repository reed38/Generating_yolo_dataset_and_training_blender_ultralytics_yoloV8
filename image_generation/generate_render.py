## Import all relevant libraries
import sys
import math
import random
import time
from typing import *
import bpy
import numpy as np
import math as m
import os
import json
import jsonschema

# # Allow other computers to attach to ptvsd at this IP address and port.
# ptvsd.enable_attach(address=('localhost', 3000))

# # Pause the program until a remote debugger is attached
# ptvsd.wait_for_attach()



#######################Main code##############################################
class BlenderGenerator:
    def __init__(self,config_path:str, config_schema_path:str, config_name:str,render_counter:int):
        
        self.config_path=config_path
        self.config_schema_path=config_schema_path
        self.config_name=config_name
        self.load_config()
        self.init_file_project_file_structure()
        self.init_scene()
        self.render_counter:int=render_counter
        
    def init_scene(self):
        """ this function is used to initialize a scene with the necessary elements"""


        ## we start by deleting default ressources in blender

        # Remove all mesh objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()

        # Remove all mesh data
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)

        # Remove all materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

        # Remove all textures
        for texture in bpy.data.textures:
            bpy.data.textures.remove(texture)

        # Remove all lights
        for light in bpy.data.lights:
            bpy.data.lights.remove(light)

        # Remove all cameras
        for camera in bpy.data.cameras:
            bpy.data.cameras.remove(camera)

        # Remove all collections
        for collection in bpy.data.collections:
            bpy.data.collections.remove(collection)


        #we then add our ressources to the scene
        scene = bpy.data.scenes.get('Scene')
        if scene is None:
            scene = bpy.data.scenes.new('Scene')
        self.scene=scene

        #adding the camera
        camera = bpy.data.objects.get('Camera')
        if camera is None:
            camera_data = bpy.data.cameras.new('Camera')
            camera = bpy.data.objects.new('Camera', camera_data)
            scene.collection.objects.link(camera)
        self.camera=camera
        bpy.context.scene.camera = camera
        
        #adding light 1
        light_1 = bpy.data.objects.get('Light1')
        if light_1 is None:
            light_data_1 = bpy.data.lights.new('Light1', 'POINT')
            light_1 = bpy.data.objects.new('Light1', light_data_1)
            scene.collection.objects.link(light_1)
        self.light_1=light_1
        
        #adding light2
        light_2 = bpy.data.objects.get('Light2')
        if light_2 is None:
            light_data_2 = bpy.data.lights.new('Light2', 'POINT')
            light_2 = bpy.data.objects.new('Light2', light_data_2)
            scene.collection.objects.link(light_2)
        self.light_2=light_2

        #adding the object
        bpy.ops.wm.collada_import(filepath= os.path.join(self.objects_folder,self.object_path))
        
        # Get the name of the last imported object 
        imported_object = bpy.context.selected_objects[-1]
        self.object=imported_object
        self.object_name=imported_object.name
        #change the location of the object to the origin 
        imported_object.location = (0.0, 0.0, 0.0)

        #adding the plane on which the object is put
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        # Get the plane object
        plane = bpy.context.object
        # Set the plane as an attribute of the class
        self.ground=plane
        # Change the location of the plane
        plane.location = (0, 0,-0.01 ) 
        # Change the size of the plane
        plane.scale = (10,10,10)  # Replace with your desired scale
        
    def load_config(self):
        # Load the JSON schema
        with open(self.config_schema_path) as schema_file:
            schema = json.load(schema_file)

        with open(self.config_path) as json_file:
            try:
                #verrifying the config file is valid
                configs = json.load(json_file)
                jsonschema.validate(instance=configs, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError("the configuration json file is incorrect file: " + str(e))

        # Extract the configuration values
        for config in configs:
            if config['id'] == self.config_name:
                self.classe = config['classe']
                self.image_width = config['image_width']
                self.image_height = config['image_height']
                self.render_percentage = config['render_percentage']
                self.samples_number = config['samples_number']
                self.object_path = config['object_path']
                self.render_number = config['render_number']
                self.radiusVariation = config['radiusVariation']
                self.angleBetaVariation = config['angleBetaVariation']
                self.angleTetaVariation = config['angleTetaVariation']
                self.angleRohVariation = config['angleRohVariation']
                self.heightVariation = config['heightVariation']
                break
        else:
            raise ValueError(f"No configuration found with id {self.config_name}")
    
    def init_file_project_file_structure(self):

        
        self.project_directory_path = os.path.join(os.getcwd(),"result",self.config_name)
        print(f"project directory path : {self.project_directory_path}")
        os.makedirs(self.project_directory_path, exist_ok=True)

        # Create the subdirectories
        
        subdirectories = ['blender', 'dataset/all', 'dataset/images', 'dataset/labels', 'yolo']
        for subdir in subdirectories:
            os.makedirs(os.path.join(self.project_directory_path, subdir), exist_ok=True)

        # Change the current working directory to the 'blender' directory
        
        self.renders_folder=os.path.join(self.project_directory_path, "dataset/images")
        self.labels_folder=os.path.join(self.project_directory_path, "dataset/labels")
        self.ground_folder=os.path.join(os.getcwd(),"ground")
        self.objects_folder=os.path.join(os.getcwd(),"objects")
        print(f"current dir: {os.getcwd()}")

    def generate_key_frames(self):
        self.keyframes = []

        frameCounter:int=0
        increment:int=int((self.render_number)**(1/3))
        start_time = time.time()
        for height_cm in range(self.heightVariation["min"], self.heightVariation["max"], int((self.heightVariation["max"]-self.heightVariation["min"])/increment)):
            for radius_cm in range(self.radiusVariation["min"], self.radiusVariation["max"],int((self.radiusVariation["max"]-self.radiusVariation["min"])/increment)):
                radius_m = radius_cm / 100
                height_m = height_cm / 100
                
                for angleRoh in range(self.angleRohVariation["min"], self.angleRohVariation["max"],int((self.angleRohVariation["max"]-self.angleRohVariation["min"])/increment)):

                    # Calculate the x, y, and z coordinates for the camera
                    x = radius_m * math.cos(math.radians(angleRoh))
                    y = radius_m * math.sin(math.radians(angleRoh))
                    z = bpy.data.objects.get(self.object_name).location.z + height_m  # Add the height to the object's current z-coordinate

                    # Set the camera's location
                    self.camera.location = (x, y, z)

                    # Make the camera look at the cube
                    direction = self.object.location - self.camera.location
                    rot_quat = direction.to_track_quat('-Z', 'Y')

                    # Convert the quaternion to Euler angles
                    euler = rot_quat.to_euler()

                    # Add a small random offset to the Euler angles
                    euler.x += math.radians(random.uniform(self.angleTetaVariation["min"], self.angleTetaVariation["max"]))
                    euler.y += math.radians(random.uniform(self.angleBetaVariation["min"], self.angleBetaVariation["max"]))
                    euler.z += math.radians(random.uniform(-5,5 ))

                    # Set the camera's rotation
                    self.camera.rotation_euler = euler

                    # Create a dictionary to represent the keyframe
                    keyframe = {
                        "frame": frameCounter,
                        "location": (x, y, z),
                        "rotation": euler.copy()  # Make sure to copy the Euler object
                    }

                    # Add the keyframe to the list
                    self.keyframes.append(keyframe)
                    frameCounter += 1

                    # Calculate the percentage of completion
                    percent_complete = frameCounter / self.render_number * 100
                    # Calculate the elapsed time
                    elapsed_time = time.time() - start_time
                    # Estimate the remaining time
                    time_per_iteration = elapsed_time / frameCounter
                    remaining_iterations = self.render_number - frameCounter
                    estimated_remaining_time = time_per_iteration * remaining_iterations
                    hours, remainder = divmod(estimated_remaining_time, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    # Print the progress information to the terminal
                    print(f"Progress key frame generation for {self.config_name}:: {percent_complete:.2f}% complete, estimated remaining time: {int(hours)}:{int(minutes)}:{seconds:.2f}", end='\r')

    def set_random_ground(self):

        # take a random ground texture
        ground_path_list = [os.path.join(self.ground_folder, file) for file in os.listdir(self.ground_folder)]        
        random_ground_texture = random.choice(ground_path_list)



        # Check if the ground object already has a material
        if self.ground.data.materials:
            # If it does, replace the existing material
            mat_sol = self.ground.data.materials[0]
        else:
            # If it doesn't, create a new material and append it
            mat_sol = bpy.data.materials.new(name="Sol_Material")
            self.ground.data.materials.append(mat_sol)
            # Ajouter une texture pour le sol
        if self.ground and self.ground.data.materials:
            mat_sol.use_nodes = True
            nodes = mat_sol.node_tree.nodes
            principled_bsdf = nodes.get("Principled BSDF")
            if principled_bsdf:
                texture_node = nodes.new('ShaderNodeTexImage')
                texture_node.image = bpy.data.images.load(random_ground_texture)  # adding rhe randomly chosen image path
                
                # Ajouter un nœud de texture de coordonnées générées
                texture_coord_node = nodes.new('ShaderNodeTexCoord')
                
                # Ajouter un nœud de texture de répétition
                texture_repeat_node = nodes.new('ShaderNodeMapping')
                texture_repeat_node.inputs['Location'].default_value[0] = 0
                texture_repeat_node.inputs['Location'].default_value[1] = 0
                texture_repeat_node.inputs['Scale'].default_value[0] = random.uniform(4, 8)  # Nombre de répétitions en X
                texture_repeat_node.inputs['Scale'].default_value[1] = random.uniform(4, 8)  # Nombre de répétitions en Y
                
                # Connecter les nœuds
                mat_sol.node_tree.links.new(texture_coord_node.outputs['Generated'], texture_repeat_node.inputs['Vector'])
                mat_sol.node_tree.links.new(texture_repeat_node.outputs['Vector'], texture_node.inputs['Vector'])
                mat_sol.node_tree.links.new(texture_node.outputs['Color'], principled_bsdf.inputs['Base Color'])
        
    
################################## Add the keyframes to Blender#####################################################
    def InsertKeyFrame(self):
        keyFrameCounter:int=0
        total_iterations=len(self.keyframes)
        start_time = time.time()
        for keyframe in self.keyframes:
            keyFrameCounter+=1
            self.camera.location = keyframe["location"]
            self.camera.rotation_euler = keyframe["rotation"]
            self.camera.keyframe_insert(data_path="location", frame=keyframe["frame"])
            self.camera.keyframe_insert(data_path="rotation_euler", frame=keyframe["frame"])
            # Calculate the percentage of completion for key frame insertion
            percent_complete = keyFrameCounter / total_iterations * 100
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            # Estimate the remaining time
            time_per_iteration = elapsed_time / keyFrameCounter
            remaining_iterations = total_iterations - keyFrameCounter
            estimated_remaining_time = time_per_iteration * remaining_iterations
            hours, remainder = divmod(estimated_remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Print the progress information to the terminal
            print(f"Progress key frame insertion for {self.config_name}: {percent_complete:.2f}% complete, estimated remaining time: {int(hours)}:{int(minutes)}:{seconds:.2f}", end='\r')

#########################GENERATING RENDER##################################

    def renderFrames(self):
        FrameCounter:int=0
        start_time = time.time()
        total_iterations=len(self.keyframes)
        for keyframe in self.keyframes:
            self.render_counter += 1
            FrameCounter+=1
            self.set_random_ground()
        
            # Set the camera's location and rotation to match the keyframe
            bpy.context.scene.frame_set(keyframe['frame'])
            
            ## Configure lighting
            self.light_2.location = (random.uniform(1,5),random.uniform(1,5),random.uniform(1,5))# Set the coordinates of light_2
            self.light_1.location = (random.uniform(1,5),random.uniform(1,5),random.uniform(1,5))# Set the coordinates of light_2
            self.light_1.data.energy = random.randint(150, 600) # Update the <bpy.data.objects['Light']> energy information
            self.light_2.data.energy = random.randint(150, 600) # Update the <bpy.data.objects['Light2']> energy information
            # Set all scene parameters
            bpy.context.scene.cycles.samples = self.samples_number
            self.scene.render.resolution_x = self.image_width
            self.scene.render.resolution_y = self.image_height
            self.scene.render.resolution_percentage = self.render_percentage
            self.scene.render.filepath =  os.path.join(self.renders_folder, f"{self.render_counter}.png")
            


            # Take picture of current visible scene
            bpy.ops.render.render(write_still=True)

            #Calculate the associated label
            text_file_name = self.labels_folder + '/' + str(self.render_counter) + '.txt' # Create label file name
            text_file = open(text_file_name, 'w+') # Open .txt file of the label
            
            # Get formatted coordinates of the bounding boxes of all the objects in the scene
            text_coordinates = self.get_all_coordinates()
            splitted_coordinates = text_coordinates.split('\n')[:-1] # Delete last '\n' in coordinates
            text_file.write('\n'.join(splitted_coordinates)) # Write the coordinates to the text file and output the render_counter.txt file
            text_file.close() # Close the .txt file corresponding to the label
        
        
            # Calculate the percentage of completion for key frame insertion
            percent_complete = FrameCounter / total_iterations * 100
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            # Estimate the remaining time
            time_per_iteration = elapsed_time / FrameCounter
            remaining_iterations = total_iterations - FrameCounter
            estimated_remaining_time = time_per_iteration * remaining_iterations
            
            hours, remainder = divmod(estimated_remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Print the progress information to the terminal
            print(f"Progress blender generation for {self.config_name}: {percent_complete:.2f}% complete, estimated remaining time: {int(hours)}:{int(minutes)}:{seconds:.2f}", end='\r')


    def finish_and_close(self):
        # Save the current Blender project in the 'blender' directory
        bpy.ops.wm.save_mainfile(filepath=os.path.join(self.project_directory_path, 'blender', f"{self.object_name}.blend"))
        # Close Blender
        bpy.ops.wm.quit_blender()
    
##############################FUNCTIONS USED TO GET COORDINATE OF THE OBJECT############################################
    def get_all_coordinates(self):
        '''
        This function takes no input and outputs the complete string with the coordinates
        of all the objects in view in the current image
        '''
        main_text_coordinates = '' # Initialize the variable where we'll store the coordinates
        b_box = self.find_bounding_box(self.object) # Get current object's coordinates
        if b_box: # If find_bounding_box() doesn't return None
            text_coordinates = self.format_coordinates(b_box, self.object_name) # Reformat coordinates to YOLOv3 format
            main_text_coordinates = main_text_coordinates + text_coordinates # Update main_text_coordinates variables whith each
                                                                                # line corresponding to each class in the frame of the current image

        return main_text_coordinates # Return all coordinates

    def format_coordinates(self, coordinates, classe):
        '''
        This function takes as inputs the coordinates created by the find_bounding box() function, the current class,
        the image width and the image height and outputs the coordinates of the bounding box of the current class
        '''
        # If the current class is in view of the camera
        if coordinates: 
            ## Change coordinates reference frame
            x1 = (coordinates[0][0])
            x2 = (coordinates[1][0])
            y1 = (1 - coordinates[1][1])
            y2 = (1 - coordinates[0][1])

            ## Get final bounding box information
            width = (x2-x1)  # Calculate the absolute width of the bounding box
            height = (y2-y1) # Calculate the absolute height of the bounding box
            # Calculate the absolute center of the bounding box
            cx = x1 + (width/2) 
            cy = y1 + (height/2)

            ## Formulate line corresponding to the bounding box of one class
            txt_coordinates = str(self.classe) + ' ' + str(cx) + ' ' + str(cy) + ' ' + str(width) + ' ' + str(height) + '\n'

            return txt_coordinates
        # If the current class isn't in view of the camera, then pass
        else:
            pass

    def find_bounding_box( self,obj):
        """
        Returns camera space bounding box of the mesh object.

        Gets the camera frame bounding box, which by default is returned without any transformations applied.
        Create a new mesh object based on carre_bleu and undo any transformations so that it is in the same space as the
        camera frame. Find the min/max vertex coordinates of the mesh visible in the frame, or None if the mesh is not in view.

        :param scene:
        :param camera_object:
        :param mesh_object:
        :return:
        """

        """ Get the inverse transformation matrix. """
        matrix = self.camera.matrix_world.normalized().inverted()
        """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)

        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in self.camera.data.view_frame(scene=self.scene)[:3]]

        lx = []
        ly = []

        for v in mesh.vertices:
            co_local = v.co
            z = -co_local.z

            if z <= 0.0:
                """ Vertex is behind the camera; ignore it. """
                continue
            else:
                """ Perspective division """
                frame = [(v / (v.z / z)) for v in frame]

            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y

            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)

            lx.append(x)
            ly.append(y)


        """ Image is not in view if all the mesh verts were ignored """
        if not lx or not ly:
            return None

        min_x = np.clip(min(lx), 0.0, 1.0)
        min_y = np.clip(min(ly), 0.0, 1.0)
        max_x = np.clip(max(lx), 0.0, 1.0)
        max_y = np.clip(max(ly), 0.0, 1.0)

        """ Image is not in view if both bounding points exist on the same side """
        if min_x == max_x or min_y == max_y:
            return None

        """ Figure out the rendered image size """
        render = self.scene.render
        fac = render.resolution_percentage * 0.01
        dim_x = render.resolution_x * fac
        dim_y = render.resolution_y * fac
        
        ## Verify there's no coordinates equal to zero
        coord_list = [min_x, min_y, max_x, max_y]
        if min(coord_list) == 0.0:
            indexmin = coord_list.index(min(coord_list))
            coord_list[indexmin] = coord_list[indexmin] + 0.0000001

        return (min_x, min_y), (max_x, max_y)


def main():
    current_dir:str=os.getcwd()
    config_path=os.path.join(current_dir,"conf/config.json")
    config_json_schema=os.path.join(current_dir,"conf/config_schema.json")


    # Load the JSON config file
    with open(config_path, 'r') as config_file:
        configs = json.load(config_file)  # Use config_file here, not config_path

    # Load the JSON schema
    with open(config_json_schema,'r') as schema_file:
        schema = json.load(schema_file)
    # Validate the config against the schema
    jsonschema.validate(configs, schema)
    ids = [config['id'] for config in configs]
    # Iterate through the configs

    render_counter:int=0
    for id in ids:
        objectGeneration:BlenderGenerator=BlenderGenerator(config_path=config_path,
                                                       config_schema_path=config_json_schema,
                                                        config_name=id,render_counter=render_counter)
        # Perform the operations for each config
        objectGeneration.load_config()
        objectGeneration.generate_key_frames()
        objectGeneration.InsertKeyFrame()
        objectGeneration.renderFrames()
        objectGeneration.finish_and_close()
        
        # PATH to save the results
        path1 = f"{objectGeneration.project_directory_path}/dataset/all"
        path2 = f"{os.getcwd()}/result/all_objects/dataset/"

        # Create the directories if they don't exist
        os.makedirs(path1, exist_ok=True)
        os.makedirs(path2, exist_ok=True)

        os.system(f"cp {objectGeneration.labels_folder}/* {objectGeneration.project_directory_path}/dataset/all")
        os.system(f"cp {objectGeneration.renders_folder}/* {objectGeneration.project_directory_path}/dataset/all")
        os.system(f"cp {objectGeneration.project_directory_path}/dataset/all/* {os.getcwd()}/result/all_objects/dataset/")

        render_counter=objectGeneration.render_counter+1

if __name__ == '__main__':
    main()