#version 330

in vec3 pos;
out vec4 outputColor;
void main()
{
    vec3 color = pos + vec3(0.0f, 0.0f, 1.0f - pos.x - pos.y);
    outputColor = vec4(color, 1.0f);
}
