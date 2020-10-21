#version 330
layout(location = 0) in vec4 position;

in vec3 vertexColor;

uniform mat4 mvp;

out vec3 color;

void main()
{
    color = vertexColor;
    gl_Position = mvp * position;
}
