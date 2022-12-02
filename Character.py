from Base3DObjects import *
from Sphere import *


class Character:
    def __init__(self, view_matrix, model_matrix, frame, position, rotation=0):
        self.view_matrix = view_matrix
        self.model_matrix = model_matrix

        self.print_timer = 0
        self.falling = False

        self.position = position
        self.rotation = 0
        self.last_rotation = 0

        self.up_rotation = 0
        self.last_up_rotation = 0

        self.velocity = Vector(0, 0, 0)

        self.gravity = 2.5
        self.height = 0.8
        self.curr_cell = None
        self.speed = 1
        self.on_ground = True

        self.collision_sphere = Sphere(self.position, 1, frame)

    def get_cell_position(self, maze):
        # print("{} / {}".format(self.position.x, maze.cell_size))
        return Vector(int((self.position.x / maze.cell_size)), 0,
                      int((self.position.z / maze.cell_size)))

    def get_cell_position_float(self, maze):
        return Vector(((self.position.x / maze.cell_size)), 0,
                      ((self.position.z / maze.cell_size)))

    def print_sphere_position(self):
        print("C: {},{},{}".format(self.collision_sphere.position.x,
                                   self.collision_sphere.position.y,
                                   self.collision_sphere.position.z))

    def raise_cell(self, maze):
        my_position = self.get_cell_position(maze)
        if self.velocity.x == 0 and self.velocity.z == 0:
            return None
        x_vel = 0
        z_vel = 0

        if abs(self.velocity.x) > abs(self.velocity.z):
            if self.velocity.x > 0:
                x_vel += 1
            elif self.velocity.x < 0:
                x_vel -= 1
        else:
            if self.velocity.z > 0:
                z_vel += 1
            elif self.velocity.z < 0:
                z_vel -= 1

        cell_to_raise = maze.get_cell_at_position(Vector(my_position.x + x_vel, my_position.y, my_position.z + z_vel))
        if cell_to_raise is None:
            return
        for object in cell_to_raise.objects:
            if not object.moved:
                object.moved = True

    def spawn_cell(self, maze):

        ch_position = self.get_cell_position_float(maze)
        heading_cells = self.get_heading_cells(maze, False)

        id_list = []

        if len(heading_cells) == 0:
            return None

        fraction_x = ch_position.x - int(ch_position.x)
        fraction_z = ch_position.z - int(ch_position.z)

        if fraction_x > 0.8 and heading_cells[0] != None:
            # print("spawn on x")
            id_list.append(heading_cells[0].id)
        if (len(heading_cells) > 1):
            if fraction_z > 0.8 and heading_cells[1] != None:
                # print("spawn on z")
                id_list.append(heading_cells[1].id)

        return id_list

    def move(self, delta_time):
        self.velocity.y -= self.gravity

        self.rotate(self.rotation)
        self.position += self.velocity * delta_time

        temp = self.position * 1
        temp.y += self.height

        self.view_matrix.eye = temp

        collision_temp = self.position * 1

        self.collision_sphere.position = collision_temp

    def rotate(self, angle):

        angCos = cos(radians(angle))
        angSin = sin(radians(angle))
        temp_vel_x = self.velocity.x
        self.velocity.x = self.velocity.x * angCos - self.velocity.z * angSin
        self.velocity.z = temp_vel_x * angSin + self.velocity.z * angCos

        # print("x:{}, z:{}".format(self.velocity.x, self.velocity.z))

    def intersect(self, box):
        # get box closest point to sphere center by clamping
        x = max(box.minX(), min(self.collision_sphere.position.x, box.maxX()))
        y = max(box.minY(), min(self.collision_sphere.position.y, box.maxY()))
        z = max(box.minZ(), min(self.collision_sphere.position.z, box.maxZ()))

        # this is the same as isPointInsideSphere
        distance = math.sqrt(
            (x - self.collision_sphere.position.x) * (x - self.collision_sphere.position.x) +
            (y - self.collision_sphere.position.y) * (y - self.collision_sphere.position.y) +
            (z - self.collision_sphere.position.z) * (z - self.collision_sphere.position.z)
        )
        if distance < self.collision_sphere.radius:
            # print("x:{} y:{} z:{}".format(x, y, z))
            vec = self.position - Vector(x, y, z)  # line from me to collision
            vec.normalize()
            # self.check_positions()
            vec *= self.collision_sphere.radius  # + self.collision_sphere.radius / 2
            self.position = Vector(x, y, z) + vec
            return Vector(x, y, z)

        return None

    def check_positions(self):
        if self.position != self.collision_sphere.position:
            # print("collision position and player position are not the same.")
            print("x:{} y:{} z:{}".format(self.position.x, self.position.y, self.position.z))
            print("x:{} y:{} z:{}\n\n".format(self.collision_sphere.position.x, self.collision_sphere.position.y,
                                              self.collision_sphere.position.z))
        else:
            print("coll and player are the same")

    def get_close_objects(self, maze):

        cells_to_look_at = []
        close_objects = []

        player_cell = self.get_cell_position(maze)

        heading_cells = self.get_heading_cells(maze)
        cells_to_look_at.extend(heading_cells)

        player_cell = maze.get_cell_at_position(player_cell)

        if player_cell is not None:
            cells_to_look_at.append(player_cell)

        for cell in cells_to_look_at:
            close_objects.extend(cell.objects)

        return close_objects

    def get_heading_cells(self, maze, include_empty=False):
        player_cell = self.get_cell_position(maze)

        heading_cells = []
        if self.velocity.x != 0:
            if self.velocity.x > 0:
                x_margin = 1
            elif self.velocity.x < 0:
                x_margin = -1
            x_heading_cell = Vector(player_cell.x + x_margin, 0, player_cell.z)
            if x_heading_cell.x >= 0:
                # print("loading heading cell...{},{}".format(x_heading_cell.x, x_heading_cell.z))
                x_cell = maze.get_cell_at_position(x_heading_cell)
                if x_cell != None and not include_empty:
                    heading_cells.append(x_cell)
                elif include_empty and x_cell == None:
                    heading_cells.append(x_heading_cell)
                elif include_empty:
                    heading_cells.append(None)

        if self.velocity.z != 0:
            if self.velocity.z > 0:
                z_margin = 1
            elif self.velocity.z < 0:
                z_margin = -1
            z_heading_cell = Vector(player_cell.x, 0, player_cell.z + z_margin)
            if z_heading_cell.z >= 0:
                z_cell = maze.get_cell_at_position(z_heading_cell)
                if z_cell != None and not include_empty:
                    heading_cells.append(z_cell)
                elif include_empty and z_cell == None:
                    heading_cells.append(z_heading_cell)
                elif include_empty:
                    heading_cells.append(None)

        if include_empty and len(heading_cells) == 0:
            return [None, None]
        return heading_cells

# def get_heading_cells(self, maze):
#     player_cell = self.get_cell_position(maze)
#
#     heading_cells = []
#     if self.velocity.x != 0:
#         if self.velocity.x > 0:
#             x_margin = 1
#         elif self.velocity.x < 0:
#             x_margin = -1
#         x_heading_cell = Vector(player_cell.x + x_margin, 0, player_cell.z)
#         if x_heading_cell.x >= 0:
#             # print("loading heading cell...{},{}".format(x_heading_cell.x, x_heading_cell.z))
#             x_cell = maze.get_cell_at_position(x_heading_cell)
#             if x_cell != None:
#                 heading_cells.append(x_cell)
#
#     if self.velocity.z != 0:
#         if self.velocity.z > 0:
#             z_margin = 1
#         elif self.velocity.z < 0:
#             z_margin = -1
#         z_heading_cell = Vector(player_cell.x, 0, player_cell.z + z_margin)
#         if z_heading_cell.z >= 0:
#             # print("loading heading cell...{},{}\n\n".format(z_heading_cell.x, z_heading_cell.z))
#             z_cell = maze.get_cell_at_position(z_heading_cell)
#             if z_cell != None:
#                 heading_cells.append(z_cell)
#
#     return heading_cells
#
