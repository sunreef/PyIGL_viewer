#version 330
layout(location = 0) in vec4 position;
layout(location = 1) in vec4 normal;

uniform mat4 projection;
uniform mat4 view;

out vec4 outNormal;

void main()
{
    outNormal = normal;
    outNormal.w = 0.0;
    gl_Position = projection * view * position;
}
