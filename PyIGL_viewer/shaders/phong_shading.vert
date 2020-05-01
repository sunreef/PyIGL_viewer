#version 330
layout(location = 0) in vec4 position;
layout(location = 1) in vec4 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform mat4 mvp;

out vec4 outNormal;
out vec3 worldPosition;

void main()
{
    outNormal = normal;
    outNormal.w = 0.0;
    outNormal = view * model * outNormal;
    outNormal = normalize(outNormal);
    //gl_Position = projection * view * model * position;
    worldPosition = model * position;
    gl_Position = mvp * position;
}
