#version 330
layout(location = 0) in vec4 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 color;

void main()
{
    gl_Position = projection * view * model * position;
    color = 0.5 + 0.5 * position.xyz;
}
