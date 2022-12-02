try:
    try:
        from OpenGL.GL import *  # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        print('Drat, patching for Big Sur')
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res: return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        from OpenGL.GL import *
except ImportError:
    pass
# from OpenGL.GLU import *
from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *
from Character import *
from Maze import *


class GraphicsProgram3D:
    def __init__(self):

        pygame.init()
        pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        # matrix "projection_matrix" & "view_matrix" is sent to the shader.
        self.model_matrix = ModelMatrix()
        self.projection_matrix = ProjectionMatrix()
        self.view_matrix = ViewMatrix()

        character_position = Vector(0.5, 2, 0.5)
        character_frame = self.create_cube(Point(0.5, 0.5, 0.5), Point(0, 1, 0), character_position)
        self.character = Character(self.view_matrix, self.model_matrix, character_frame, character_position)

        self.view_matrix.slide(character_position.x, character_position.y, character_position.z)

        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.projection_matrix.set_perspective(90, 16 / 9, 0.4, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.objects = []
        self.cube = Cube()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0

        self.UP_key_down = False
        self.DOWN_key_down = False
        self.RIGHT_key_down = False
        self.LEFT_key_down = False

        self.W_key_down = False
        self.A_key_down = False
        self.S_key_down = False
        self.D_key_down = False

        self.Q_key_down = False
        self.E_key_down = False
        self.R_key_down = False
        self.F_key_down = False
        self.SHIFT_key_down = False
        self.SPACE_key_down = False
        self.white_background = False

        self.init_objects()

    def init_objects(self):

        self.maze = Maze(6, 6, 4)
        self.maze.raise_height = 0
        self.maze.generate_maze()
        first_cell = self.maze.cells[0][0]
        self.maze.mouse_random(first_cell)

        self.maze.refresh_maze()

        print(self.maze.count)
        for object in self.maze.get_objects():
            self.objects.append(object)

    def create_floor(self):
        color = Point(0, 1, 0)
        position = Point(0, 0, 0)
        floor_dimensions = Vector(4, 0.1, 4)
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(position.x, position.y, position.z)
        self.model_matrix.add_scale(floor_dimensions.x, floor_dimensions.y, floor_dimensions.z)

        ret_matrix = self.model_matrix.copy_matrix()
        self.model_matrix.pop_matrix()
        new_cube = Cube(position, floor_dimensions, ret_matrix)
        new_cube.color = color
        new_cube.model_matrix = ret_matrix
        return new_cube

    def raise_objects(self, delta_time):
        for object in self.objects:
            if object.moved and not object.finished_moving:
                object.position.y += 5 * delta_time
                object.update_matrix()
                if object.object_type == "floor" and object.position.y >= self.maze.raise_height:
                    object.position.y = 0
                    object.finished_moving = True
                if object.object_type == "wall" and object.position.y >= self.maze.raise_height + self.maze.cell_size / 2:
                    object.position.y = self.maze.raise_height + self.maze.cell_size / 2
                    object.finished_moving = True

    def update_objects(self):
        id_list = self.character.spawn_cell(self.maze)
        if id_list != None:
            for id in id_list:
                for object in self.objects:
                    if object.cell_id == id and object.moved == False:
                        object.moved = True

    def perform_controls(self, delta_time):
        self.character.velocity = Vector(0, 0, 0)
        if self.W_key_down:
            self.character.velocity += Vector(0, 0, -1 * self.character.speed)
        if self.S_key_down:
            self.character.velocity += Vector(0, 0, 1 * self.character.speed)
        if self.A_key_down:
            self.character.velocity += Vector(-1 * self.character.speed, 0, 0)
        if self.D_key_down:
            self.character.velocity += Vector(1 * self.character.speed, 0, 0)

        if self.UP_key_down:
            # self.view_matrix.rotate(100 * delta_time, "pitch")
            self.character.up_rotation += 100 * delta_time
        if self.DOWN_key_down:
            # self.view_matrix.rotate(-100 * delta_time, "pitch")
            self.character.up_rotation -= 100 * delta_time
        if self.RIGHT_key_down:
            self.character.rotation += 100 * delta_time
        if self.LEFT_key_down:
            self.character.rotation += -100 * delta_time

        rotation = self.character.rotation - self.character.last_rotation
        up_rotation = self.character.up_rotation - self.character.last_up_rotation
        self.view_matrix.rotate(rotation, "yaw")
        self.view_matrix.rotate(up_rotation, "pitch")

        self.character.last_rotation = self.character.rotation
        self.character.last_up_rotation = self.character.up_rotation

        if self.Q_key_down:
            pass
            # self.view_matrix.rotate(100 * delta_time, "roll")
        if self.E_key_down:
            # self.view_matrix.rotate(-100 * delta_time, "roll")
            pass
        if self.R_key_down:
            # self.view_matrix.slide(0, 1 * delta_time, 0)
            pass
        if self.F_key_down:
            # self.view_matrix.slide(0, -1 * delta_time, 0)
            pass
        if self.SPACE_key_down and self.character.on_ground == True:
            self.character.velocity += Vector(0, self.character.height * 20, 0)
            self.character.on_ground = False
        # print(self.character.velocity.y)
        if self.SHIFT_key_down:
            self.character.speed = 5
        else:
            self.character.speed = 1
        if self.character.position.y <= 1.30:
            self.character.on_ground = True

        self.character.move(delta_time)

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        self.angle += pi * delta_time

        self.perform_controls(delta_time)
        self.camera_wall_collision()
        self.character.raise_cell(self.maze)
        self.raise_objects(delta_time)

    def create_cube(self, size, color, position):

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(position.x, position.y, position.z)
        self.model_matrix.add_scale(size.x, size.y, size.z)
        ret_matrix = self.model_matrix.copy_matrix()
        self.model_matrix.pop_matrix()

        new_cube = Cube(position, size, ret_matrix)
        new_cube.color = color

        return new_cube

    def draw_objects(self):
        for cube in self.objects:
            # if cube.moved == True:
            # print("drawing")
            self.model_matrix.stack.append(cube.model_matrix)

            self.shader.set_model_matrix(cube.model_matrix)

            self.shader.set_view_matrix(self.view_matrix.get_matrix())
            self.shader.setMaterialSpecular(cube.color.x, cube.color.y, cube.color.z, 0)
            self.shader.setMaterialSpecular(cube.color.x, cube.color.y, cube.color.z, 1)
            self.shader.setMaterialSpecular(cube.color.x, cube.color.y, cube.color.z, 2)
            self.shader.setMaterialSpecular(cube.color.x, cube.color.y, cube.color.z, 3)

            self.shader.setShineSpecular(1, 0)
            self.shader.setShineSpecular(1, 1)
            self.shader.setMaterialDiffuse(cube.color.x, cube.color.y, cube.color.z, 0)
            self.shader.setMaterialDiffuse(cube.color.x, cube.color.y, cube.color.z, 1)
            self.shader.setMaterialDiffuse(cube.color.x, cube.color.y, cube.color.z, 2)
            self.shader.setMaterialDiffuse(cube.color.x, cube.color.y, cube.color.z, 3)

            self.cube.draw(self.shader)

            self.model_matrix.pop_matrix()

    def camera_wall_collision(self):

        objects_to_check = self.character.get_close_objects(self.maze)

        for box in objects_to_check:
            self.character.intersect(box)

    def display(self):
        glEnable(
            GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)

        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)

        glClear(
            GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, 800, 600)

        # specular light 1
        p_position = self.character.position
        self.shader.setLightPosition(Vector(5, 10, 0), 0)
        self.shader.setLightSpecular(1, 1, 1, 0)

        # specular light 2
        self.shader.setLightPosition(Vector(p_position.x, p_position.y, p_position.z), 1)
        self.shader.setLightSpecular(1, 0, 1, 1)

        # specular light 3
        self.shader.setLightPosition(Vector(0, 10, 5), 2)
        self.shader.setLightSpecular(1, 1, 1, 2)

        # specular light 4
        self.shader.setLightPosition(Vector(p_position.x, p_position.y + 10, p_position.z), 3)
        self.shader.setLightSpecular(1, 1, 0, 3)

        # diffuse light 1
        self.shader.setLightDiffuse(1, 1, 1, 0)

        # diffuse light 2
        self.shader.setLightDiffuse(0, 1, 1, 1)

        # drawing the floor
        self.draw_objects()

        pygame.display.flip()

    def program_loop(self):
        exiting = False

        while not exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True

                    # if event.key == K_UP:
                    #     self.UP_key_down = True
                    # if event.key == K_DOWN:
                    #    self.DOWN_key_down = True
                    if event.key == K_LEFT:
                        self.LEFT_key_down = True
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = True

                    if event.key == K_w:
                        self.W_key_down = True
                    if event.key == K_s:
                        self.S_key_down = True
                    if event.key == K_a:
                        self.A_key_down = True
                    if event.key == K_d:
                        self.D_key_down = True

                    if event.key == K_q:
                        self.Q_key_down = True
                    if event.key == K_e:
                        self.E_key_down = True
                    if event.key == K_r:
                        self.R_key_down = True
                    if event.key == K_f:
                        self.F_key_down = True
                    if event.key == K_SPACE:
                        self.SPACE_key_down = True
                    if event.key == K_LSHIFT:
                        self.SHIFT_key_down = True

                elif event.type == pygame.KEYUP:

                    if event.key == K_UP:
                        self.UP_key_down = False
                    if event.key == K_DOWN:
                        self.DOWN_key_down = False
                    if event.key == K_LEFT:
                        self.LEFT_key_down = False
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = False
                    if event.key == K_w:
                        self.W_key_down = False
                    if event.key == K_s:
                        self.S_key_down = False
                    if event.key == K_a:
                        self.A_key_down = False
                    if event.key == K_d:
                        self.D_key_down = False
                    if event.key == K_q:
                        self.Q_key_down = False
                    if event.key == K_e:
                        self.E_key_down = False
                    if event.key == K_r:
                        self.R_key_down = False
                    if event.key == K_f:
                        self.F_key_down = False
                    if event.key == K_SPACE:
                        self.SPACE_key_down = False
                    if event.key == K_LSHIFT:
                        self.SHIFT_key_down = False

            self.update()
            self.display()

        # OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
