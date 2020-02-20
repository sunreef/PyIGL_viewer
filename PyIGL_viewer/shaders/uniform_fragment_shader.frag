#version 330

uniform vec3 albedo;

out vec4 outputColor;
void main()
{
    outputColor = vec4(albedo, 1.0f);
}
