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
from OpenGL.GLU import *

import math
import numpy as np
from math import *


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)


# point to point (a line)
class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        length = self.__len__()
        self.x /= length
        self.y /= length
        self.z /= length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def ortho(self):
        temp_x = self.x
        self.x = -self.y
        self.y = temp_x

    def distance(self, other):
        eq1 = pow(other.x - self.x, 2)
        eq2 = pow(other.y - self.y, 2)
        eq3 = pow(other.z - self.z, 2)
        return sqrt(eq1 + eq2 + eq3)


class Cube:
    def __init__(self, position=Vector(0, 0, 0), dimensions=Vector(0, 0, 0), cell_id=-1):
        self.position_array = [-0.5, -0.5, -0.5,
                               -0.5, 0.5, -0.5,
                               0.5, 0.5, -0.5,
                               0.5, -0.5, -0.5,

                               -0.5, -0.5, 0.5,
                               -0.5, 0.5, 0.5,
                               0.5, 0.5, 0.5,
                               0.5, -0.5, 0.5,

                               -0.5, -0.5, -0.5,
                               0.5, -0.5, -0.5,
                               0.5, -0.5, 0.5,
                               -0.5, -0.5, 0.5,

                               -0.5, 0.5, -0.5,
                               0.5, 0.5, -0.5,
                               0.5, 0.5, 0.5,
                               -0.5, 0.5, 0.5,

                               -0.5, -0.5, -0.5,
                               -0.5, -0.5, 0.5,
                               -0.5, 0.5, 0.5,
                               -0.5, 0.5, -0.5,

                               0.5, -0.5, -0.5,
                               0.5, -0.5, 0.5,
                               0.5, 0.5, 0.5,
                               0.5, 0.5, -0.5]

        self.normal_array = [0.0, 0.0, -1.0,
                             0.0, 0.0, -1.0,
                             0.0, 0.0, -1.0,
                             0.0, 0.0, -1.0,
                             0.0, 0.0, 1.0,
                             0.0, 0.0, 1.0,
                             0.0, 0.0, 1.0,
                             0.0, 0.0, 1.0,
                             0.0, -1.0, 0.0,
                             0.0, -1.0, 0.0,
                             0.0, -1.0, 0.0,
                             0.0, -1.0, 0.0,
                             0.0, 1.0, 0.0,
                             0.0, 1.0, 0.0,
                             0.0, 1.0, 0.0,
                             0.0, 1.0, 0.0,
                             -1.0, 0.0, 0.0,
                             -1.0, 0.0, 0.0,
                             -1.0, 0.0, 0.0,
                             -1.0, 0.0, 0.0,
                             1.0, 0.0, 0.0,
                             1.0, 0.0, 0.0,
                             1.0, 0.0, 0.0,
                             1.0, 0.0, 0.0]

        self.color = Point(0, 1, 0)

        self.position = position
        self.dimensions = dimensions

        self.model_matrix = [1, 0, 0, self.position.x,
                             0, 1, 0, self.position.y,
                             0, 0, 1, self.position.z,
                             0, 0, 0, 1]

        self.cell_id = cell_id
        self.moved = False
        self.finished_moving = False
        self.object_type = None

        # print(self.lines)

    def add_transformation(self, matrix2):
        counter = 0
        new_matrix = [0] * 16
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += self.model_matrix[row * 4 + i] * matrix2[col + 4 * i]
                counter += 1
        self.model_matrix = new_matrix

    def add_translation(self, x, y, z):
        other_matrix = [1, 0, 0, x,
                        0, 1, 0, y,
                        0, 0, 1, z,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def update_matrix(self):
        # print(self.position.x, self.position.y)
        self.model_matrix[3] = self.position.x
        self.model_matrix[7] = self.position.y
        self.model_matrix[11] = self.position.z
        # self.add_translation(self.position.x, self.position.y, self.position.z)
        # self.model_matrix.add_scale(size.x, size.y, size.z)

    def draw(self, shader):
        shader.set_position_attribute(self.position_array)
        shader.set_normal_attribute(self.normal_array)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 4, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 8, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 12, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 16, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 20, 4)

    def maxX(self):
        return self.position.x + self.dimensions.x / 2

    def maxY(self):
        return self.position.y + self.dimensions.y / 2

    def maxZ(self):
        return self.position.z + self.dimensions.z / 2

    def minX(self):
        return self.position.x - self.dimensions.x / 2

    def minY(self):
        return self.position.y - self.dimensions.y / 2

    def minZ(self):
        return self.position.z - self.dimensions.z / 2
