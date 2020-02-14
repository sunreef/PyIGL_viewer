#version 330

in vec4 color;
in vec4 outNormal;

uniform vec3 lightDirection;
uniform vec3 lightIntensity;
uniform vec3 ambientLighting;

out vec4 outputColor;
void main()
{
    float dot_normal = abs(dot(outNormal.xyz, lightDirection));
    vec3 finalColor = ambientLighting;
    finalColor += dot_normal * lightIntensity;
    finalColor *= color.xyz;
    outputColor = vec4(finalColor, color.w);
}
