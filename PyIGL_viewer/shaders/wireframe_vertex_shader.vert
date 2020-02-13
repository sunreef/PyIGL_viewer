#version 330
layout(location = 0) in vec4 position;

uniform mat4 projection;
uniform mat4 view;

float EPSILON = 1e-4;

void main()
{
    gl_Position = projection * view * position;
    gl_Position.z -= EPSILON;
}
