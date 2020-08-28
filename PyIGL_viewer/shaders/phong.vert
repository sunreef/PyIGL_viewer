
#version 330
layout(location = 0) in vec4 position;
in vec4 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform mat4 mvp;

uniform bool linkLight;
uniform vec3 lightDirection;

out vec4 outNormal;
out vec4 worldPosition;
out vec3 transformedLightDirection;

void main()
{
    outNormal = normal;
    outNormal.w = 0.0;
    outNormal = model * outNormal;
    outNormal = normalize(outNormal);
    if (linkLight) {
        transformedLightDirection = (inverse(view) * vec4(lightDirection, 0.0)).xyz;
    }
    else {
        transformedLightDirection = lightDirection;
    }
    worldPosition = position;
    gl_Position = mvp * position;
}
