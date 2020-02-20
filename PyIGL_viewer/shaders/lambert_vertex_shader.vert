#version 330
layout(location = 0) in vec4 position;
layout(location = 1) in vec4 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec4 outNormal;

void main()
{
    outNormal = normal;
    outNormal.w = 0.0;
    outNormal = model * outNormal;
    gl_Position = projection * view * model * position;
}
