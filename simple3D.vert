attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 projection_view_matrix;

uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;



const int number_of_lights = 4;

uniform vec4 eye_position;

uniform vec4 u_light_position[number_of_lights];
uniform vec4 u_light_diffuse[number_of_lights];
uniform vec4 u_material_diffuse[number_of_lights];

//uniform vec4 u_light_specular;
//uniform vec4 u_material_specular;
//uniform float u_material_shininess;

varying vec4 v_color;//Leave the varying variables alone to begin with
/*
struct light {
    uniform vec4 light_position;
    uniform vec4 material_specular;
    uniform vec4 material_shininess;
};
*/

uniform float u_material_shininess[number_of_lights];
uniform vec4 u_material_specular[number_of_lights];
uniform vec4 u_light_specular[number_of_lights];

void main(void)
{

    vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
    vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);

    position = u_model_matrix * position;
    normal = u_model_matrix * normal;

    v_color = vec4(0, 0, 0, 0);
    for (int i = 0; i < 2; i++){
        vec4 s = normalize(u_light_position[i] - position);
        float lambert = max(dot(normal, s), 0.0);

        vec4 v = normalize(eye_position - position);
        vec4 h = normalize(s + v);
        float phong = max(dot(normal, h), 0.0);

        v_color += lambert * u_light_diffuse[i] * u_material_diffuse[i]
        + pow(phong, u_material_shininess[i]) * u_light_specular[i] * u_material_specular[i];
    }




    position = u_view_matrix * position;
    position = u_projection_matrix * position;

    gl_Position = position;
}