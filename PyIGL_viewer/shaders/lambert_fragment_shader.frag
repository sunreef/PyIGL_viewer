#version 330

in vec4 outNormal;

uniform vec3 albedo;
uniform vec3 lightDirection;
uniform vec3 lightIntensity;
uniform vec3 ambientLighting;

out vec4 outputColor;
void main()
{
    float dot_normal = - dot(outNormal.xyz, lightDirection);
    vec3 color = ambientLighting;
    color += dot_normal * lightIntensity;
    color *= albedo;
    outputColor = vec4(color, 1.0f);
}
