from Base3DObjects import *
import random
from Cell import *


class Maze:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height

        self.cell_size = cell_size
        self.cells = []
        self.count = 0
        self.start_position = Vector(cell_size / 2, 0, cell_size / 2)  # start in the corner

        # for mouse algo
        self.player_start_location = Vector(1, 0, 0)  # start location of maze (in maze coordinates)

        self.x_margin = 0
        self.y_margin = 0
        self.extra_cells = 0
        self.raise_height = 10

    def refresh_maze(self):
        for columns in self.cells:
            for cell in columns:
                cell.refresh_objects()

    def generate_maze(self):
        self.x_margin = self.start_position.x
        self.y_margin = self.start_position.z  # size (have to change this in accordance with cell "size")
        first = True
        id = 0
        for x in range(0, self.width):
            if x != 0:
                self.y_margin = self.start_position.z
                self.x_margin += 3  # scale*size /2
            column = []
            for y in range(0, self.height):
                if y != 0:
                    self.y_margin += 3

                color = Vector(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
                while color.__len__() < 0.8:
                    color = Vector(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))

                new_cell = Cell(color,
                                Vector(x + self.x_margin, 0, y + self.y_margin), self.cell_size,
                                Vector(x, 0, y),
                                True,
                                True,
                                id)
                id += 1
                if not first:
                    new_cell.position.y -= 10
                else:
                    first = False

                column.append(new_cell)
                self.count += 1
            self.cells.append(column)

    def cell_by_id(self, id):
        for column in self.cells:
            for cell in column:
                if cell.id == id:
                    return cell

    def get_objects(self):
        objects_in_maze = []
        for column in self.cells:
            for cell in column:
                for object in cell.objects:
                    objects_in_maze.append(object)
        return objects_in_maze

    def get_cell_at_position(self, cell_position):
        if cell_position.x > self.width or cell_position.z > self.height:
            return None
        if cell_position.x < 0 or cell_position.z < 0:
            return None

        try:
            return self.cells[cell_position.x][cell_position.z]
        except IndexError or TypeError:
            # print("ERROR: position:\n({},{})".format(cell_position.x, cell_position.z))
            return None

    def mouse_random(self, curr_cell):

        curr_cell.visited = True

        curr_location = curr_cell.maze_position
        cell_list = []

        right_location = Vector(curr_location.x - 1, 0, curr_location.z)
        right_cell = self.get_cell_at_position(right_location)
        if right_cell is not None:
            cell_list.append(right_cell)

        left_location = Vector(curr_location.x + 1, 0, curr_location.z)
        left_cell = self.get_cell_at_position(left_location)
        if left_cell is not None:
            cell_list.append(left_cell)

        up_location = Vector(curr_location.x, 0, curr_location.z + 1)
        up_cell = self.get_cell_at_position(up_location)
        if up_cell is not None:
            cell_list.append(up_cell)

        down_location = Vector(curr_location.x, 0, curr_location.z - 1)
        down_cell = self.get_cell_at_position(down_location)
        if down_cell is not None:
            cell_list.append(down_cell)

        random.shuffle(cell_list)

        for cell in cell_list:
            if not cell.visited:

                if cell.maze_position.z < curr_cell.maze_position.z:  # if new cell is below
                    curr_cell.southWall = False
                elif cell.maze_position.z > curr_cell.maze_position.z:  # if new cell is above
                    cell.southWall = False

                if cell.maze_position.x < curr_cell.maze_position.x:  # if new cell is to the left
                    curr_cell.westWall = False  # take down my right wall
                elif cell.maze_position.x > curr_cell.maze_position.x:  # if new cell is to the right
                    cell.westWall = False  # take new cells right wall

                self.mouse_random(cell)

    def mouse(self, curr_location):

        curr_cell = self.get_cell_at_position(curr_location)

        right_location = Vector(curr_location.x - 1, 0, curr_location.z)
        right_cell = self.get_cell_at_position(right_location)
        if right_cell is not None and not right_cell.visited:
            right_cell.visited = True
            right_cell.westWall = False
            self.mouse(right_location)

        left_location = Vector(curr_location.x + 1, 0, curr_location.z)
        left_cell = self.get_cell_at_position(left_location)
        if left_cell is not None and not left_cell.visited:
            left_cell.visited = True
            curr_cell.westWall = False
            self.mouse(left_location)

        up_location = Vector(curr_location.x, 0, curr_location.z + 1)
        up_cell = self.get_cell_at_position(up_location)
        if up_cell is not None and not up_cell.visited:
            up_cell.visited = True
            curr_cell.southWall = False
            self.mouse(up_location)

        down_location = Vector(curr_location.x, 0, curr_location.z - 1)
        down_cell = self.get_cell_at_position(down_location)
        if down_cell is not None and not down_cell.visited:
            down_cell.visited = True
            up_cell.southWall = False
            self.mouse(down_location)

        return
