#version 330
layout(location = 0) in vec4 position;
in vec4 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform mat4 mvp;

uniform bool linkLight;

out vec4 outNormal;

void main()
{
    outNormal = normal;
    outNormal.w = 0.0;
    outNormal = model * outNormal;
    if (linkLight) {
        outNormal = view * outNormal;
    }
    outNormal = normalize(outNormal);
    //gl_Position = projection * view * model * position;
    gl_Position = mvp * position;
}
