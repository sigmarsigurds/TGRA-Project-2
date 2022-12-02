from Base3DObjects import *
from Matrices import *


class Cell:
    def __init__(self, color, position, size, maze_position=Vector(0, 0, 0), southWall=False, westWall=False, id=0):
        self.id = id
        self.color = color
        self.southWall = southWall
        self.westWall = westWall
        self.maze_position = maze_position
        self.position = position
        self.size = size
        self.scale = 1
        self.wall_dimensions = Vector(self.size * self.scale, self.size * self.scale, 0.3)
        self.floor_dimensions = Vector(self.size * self.scale, 0.3, self.size * self.scale)
        self.model_matrix = ModelMatrix()

        self.objects = [self.create_floor()]
        self.up = False
        self.done_moving = False
        if self.southWall:
            self.objects.append(self.create_south_wall())
        if self.westWall:
            self.objects.append(self.create_west_wall())

        self.visited = False

    def refresh_objects(self):
        self.objects = [self.create_floor()]
        if self.southWall:
            self.objects.append(self.create_south_wall())
        if self.westWall:
            self.objects.append(self.create_west_wall())

    def create_south_wall(self):
        self.model_matrix.push_matrix()
        south_wall_position = Vector(self.position.x, self.position.y + self.size / 2 * self.scale,
                                     self.position.z - self.size / 2 * self.scale)

        self.model_matrix.add_translation(south_wall_position.x, south_wall_position.y, south_wall_position.z)

        self.model_matrix.add_scale(self.wall_dimensions.x, self.wall_dimensions.y, self.wall_dimensions.z)

        ret_matrix = self.model_matrix.copy_matrix()
        self.model_matrix.pop_matrix()
        new_cube = Cube(south_wall_position, self.wall_dimensions)
        new_cube.object_type = "wall"
        new_cube.color = self.color
        new_cube.model_matrix = ret_matrix
        new_cube.cell_id = self.id
        # print("cube: x: {} y:{} z:{}".format(new_cube.maxX(), new_cube.maxY(), new_cube.maxZ()))
        # print("cube: x: {} y:{} z:{}".format(new_cube.minX(), new_cube.minY(), new_cube.minZ()))
        return new_cube

    def create_west_wall(self):
        self.model_matrix.push_matrix()
        west_wall_position = Vector(self.position.x - self.size / 2 * self.scale,
                                    self.position.y + self.size / 2 * self.scale,
                                    self.position.z)
        # gæti verið vestur
        self.model_matrix.add_translation(west_wall_position.x, west_wall_position.y, west_wall_position.z)

        self.model_matrix.add_scale(self.wall_dimensions.z, self.wall_dimensions.y,
                                    self.wall_dimensions.x)

        west_wall_dimensions = Vector(self.wall_dimensions.z, self.wall_dimensions.y, self.wall_dimensions.x)
        ret_matrix = self.model_matrix.copy_matrix()
        self.model_matrix.pop_matrix()
        new_cube = Cube(west_wall_position, west_wall_dimensions)
        new_cube.object_type = "wall"
        new_cube.cell_id = self.id
        new_cube.color = self.color
        new_cube.model_matrix = ret_matrix
        return new_cube

    def create_floor(self):
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.position.x, self.position.y, self.position.z)
        self.model_matrix.add_scale(self.floor_dimensions.x, self.floor_dimensions.y, self.floor_dimensions.z)

        ret_matrix = self.model_matrix.copy_matrix()
        self.model_matrix.pop_matrix()
        new_cube = Cube(self.position, self.floor_dimensions)
        new_cube.object_type = "floor"
        new_cube.cell_id = self.id
        new_cube.color = self.color
        new_cube.model_matrix = ret_matrix
        return new_cube
