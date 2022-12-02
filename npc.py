from Base3DObjects import *


class Npc:
    def __init__(self, position, frame, model_matrix, view_matrix):
        self.position = position
        self.frame = frame

        self.model_matrix = model_matrix
        self.view_matrix = view_matrix

    def move(self, velocity, delta_time):
        self.position += velocity * delta_time
        # print("npc position: {},{},{}".format(self.position.x, self.position.y, self.position.z))

    def draw(self):
        self.model_matrix.stack.append(self.frame.model_matrix)

        self.shader.set_model_matrix(self.model_matrix.matrix)

        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.cube.draw(self.shader)
        self.shader.set_solid_color(self.frame.color.x, self.frame.color.y, self.frame.color.z)
        self.model_matrix.pop_matrix()

    # self.model_matrix.push_matrix()
    #         self.model_matrix.add_translation(1, 0.5, -3)  ### --- ADD PROPER TRANSFORMATION OPERATIONS --- ###
    #         self.shader.set_model_matrix(self.model_matrix.matrix)
    #
    #         self.shader.set_view_matrix(self.view_matrix.get_matrix())
    #
    #         self.cube.draw(self.shader)
    #         self.shader.set_solid_color(1, 0.0, 0.0)
    #         self.model_matrix.pop_matrix()
