#version 330
layout(location = 0) in vec4 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform mat4 mvp;

void main()
{
    gl_Position = mvp * position;
}
