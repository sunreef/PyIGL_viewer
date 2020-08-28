
#version 330

in vec4 outNormal;
in vec4 worldPosition;
in vec3 transformedLightDirection;

uniform vec3 cameraPosition;

uniform vec3 lightIntensity;
uniform vec3 ambientLighting;

uniform vec3 k_specular;
uniform vec3 k_diffuse;
uniform vec3 k_ambient;
uniform float shininess;

out vec4 outputColor;

void main()
{
    vec3 cameraDirection = normalize(cameraPosition - worldPosition.xyz);
    vec3 normal = outNormal.xyz;
    float dotCamera = dot(normal, cameraDirection);
    if (dotCamera < 0) {
        normal = -normal;
    }
    float dotNormal = dot(normal, -transformedLightDirection);
    vec3 reflectedRay = normalize(2.0 * dotNormal * normal + transformedLightDirection);

    float reflectedFactor = max(0.0, dot(cameraDirection, reflectedRay));
    
    vec3 ambientComponent = k_ambient * ambientLighting;
    vec3 diffuseComponent = k_diffuse * dotNormal * lightIntensity;
    vec3 specularComponent = k_specular * pow(reflectedFactor, shininess) * lightIntensity;
    outputColor = vec4(ambientComponent + diffuseComponent + specularComponent, 1.0f);
}
