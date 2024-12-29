from linalg import vec3
from python.oklch.oklch_color import OKLCH
print("100_rgb_oklch")

oklch_vec = vec3(0.8233, 0.37, 153)
lrgb_vec = vec3(0.99961, 0.52105, 0.99958)
oklch_color = OKLCH(oklch_vec)

print(oklch_color)
print(oklch_color.to_OKLAB())
print(oklch_color.to_RGB())

from python.oklch.colorcvt import *
print("\ncolorcvt module test\n",'*'*20)
print("OKLCH -> LRGB, ", oklch_to_linear_srgb(oklch_vec))
print("LRGB -> OKLCH, ", linear_srgb_to_oklch(lrgb_vec))
