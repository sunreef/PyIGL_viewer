#version 330

in vec4 outNormal;
in vec4 worldPosition;

uniform vec3 cameraPosition;

uniform vec3 lightDirection;
uniform vec3 lightIntensity;
uniform vec3 ambientLighting;

uniform vec3 specular;
uniform vec3 diffuse;
uniform vec3 ambient;
uniform float shininess;

out vec4 outputColor;

void main()
{
    vec3 ambientComponent = ambient * ambientLighting;

    float dotNormal = dot(outNormal.xyz, -lightDirection);
    vec3 diffuseComponent = diffuse * dotNormal * lightIntensity;

    vec3 reflectedDirection = 2.0 * dotNormal * outNormal.xyz + lightDirection;
    vec3 cameraVector = cameraPosition - (worldPosition.xyz / worldPosition.w);
    float dotReflected = dot(cameraVector, reflectedDirection);
    

    vec3 color = ambientLighting;
    color += dot_normal * lightIntensity;
    color *= albedo;
    outputColor = vec4(color, 1.0f);
}
