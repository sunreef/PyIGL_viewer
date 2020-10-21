#version 330
layout(location = 0) in vec4 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform mat4 mvp;

float EPSILON = 1e-6;

void main()
{
    gl_Position = mvp * position;
    gl_Position.z -= EPSILON;
}
