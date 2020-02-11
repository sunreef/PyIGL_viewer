#version 330
layout(location = 0) in vec4 position;

out vec3 pos;
void main()
{
    pos = position.xyz;
    gl_Position = position;
}
