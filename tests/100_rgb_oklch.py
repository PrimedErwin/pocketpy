from linalg import vec3
from python.oklch.oklch_color import OKLAB, OKLCH, RGB
print("100_rgb_oklch")

oklch_vec = vec3(0.8825, 0.11, 326.459)
oklch_color = OKLCH(oklch_vec)

print(oklch_color)
# print(oklch_color.to_OKLAB())
print(oklch_color.to_RGB())