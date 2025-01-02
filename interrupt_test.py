import colorcvt
from linalg import vec3

oklchc = vec3(95 / 100, 0.1381, 153)
lrgbc = colorcvt.oklch_to_linear_srgb(oklchc)
rgbc = colorcvt.linear_srgb_to_srgb(lrgbc)
print(oklchc, lrgbc, rgbc * 255)
ooklchc = colorcvt.linear_srgb_to_oklch(lrgbc)
#out of range oklch will adjust chroma
print(ooklchc)