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
from math import *  # trigonometry

import sys

from Base3DObjects import *


class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader, shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if (result != 1):  # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader, shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if (result != 1):  # shader didn't compile
            print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        self.positionLoc = glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)

        self.normalLoc = glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        self.modelMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_model_matrix")

        # self.projectionViewMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_projection_view_matrix")
        self.projectionMatrix = glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")
        self.viewMatrix = glGetUniformLocation(self.renderingProgramID, "u_view_matrix")

        self.eyePosLoc = glGetUniformLocation(self.renderingProgramID, "eye_position")

        self.lightSpecLoc = glGetUniformLocation(self.renderingProgramID, "u_light_specular")
        self.matSpecLoc = glGetUniformLocation(self.renderingProgramID, "u_material_specular")

        self.lightPosLoc = glGetUniformLocation(self.renderingProgramID, "u_light_position")
        self.lightDifLoc = glGetUniformLocation(self.renderingProgramID, "u_light_diffuse")
        self.matDifLoc = glGetUniformLocation(self.renderingProgramID, "u_material_diffuse")
        self.matShineLoc = glGetUniformLocation(self.renderingProgramID, "u_material_shininess")

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    ##def set_projection_view_matrix(self, matrix_array):
    ##  glUniformMatrix4fv(self.projectionViewMatrixLoc, 1, True, matrix_array)
    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.viewMatrix, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrix, 1, True, matrix_array)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def setLightPosition(self, pos, i):
        glUniform4f(glGetUniformLocation(self.renderingProgramID, "u_light_position[{}]".format(i)),
                    pos.x,
                    pos.y,
                    pos.z,
                    1.0)

    def setEyePosition(self, pos):
        glUniform4f(self.eyePosLoc, pos.x, pos.y, pos.z, 1.0)

    def setLightDiffuse(self, r, g, b, i):
        glUniform4f(glGetUniformLocation(self.renderingProgramID, "u_light_diffuse[{}]".format(i)), r, b, g, 0.0)

    def setLightSpecular(self, r, g, b, i):
        # "u_light[{i}]"
        glUniform4f(glGetUniformLocation(self.renderingProgramID, "u_light_specular[{}]".format(i)), r, b, g, 0.0)

    def setMaterialSpecular(self, r, g, b, i):
        glUniform4f(glGetUniformLocation(self.renderingProgramID, "u_material_specular[{}]".format(i)), r, b, g, 0.0)

    def setMaterialDiffuse(self, r, g, b, i):
        glUniform4f(glGetUniformLocation(self.renderingProgramID, "u_material_diffuse[{}]".format(i)), r, b, g, 0.0)

    def setShineSpecular(self, shininess, i):
        glUniform1f(glGetUniformLocation(self.renderingProgramID, "u_material_shininess[{}]".format(i)), shininess)
