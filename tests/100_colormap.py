from array2d import array2d
import math
import random
import colorcvt
from linalg import vec2, vec2i, vec3, vec3i
from python.colormap._cm_data import *

def ansi_bg(color: vec3i, text: str):
    r = color.x
    g = color.y
    b = color.z
    return f'\x1b[48;2;{r};{g};{b}m{text}\x1b[0m'

def valid_pos(input: vec2i, w: int, h: int) -> vec2:
    x, y = input
    if x < 0:
        x = 0
    if x > w-1:
        x = w-1
    if y < 0:
        y = 0
    if y > h-1:
        y = h-1
    return vec2(x, y)

def vec2_to_vec2i(input: vec2) -> vec2i:
    return vec2i(int(input.x), int(input.y))

def temp_map_srgb(min_temp: int, max_temp: int, curr_temp: int) -> vec3i:
    temp_range = max_temp - min_temp
    curr_temp_index = curr_temp/temp_range*len(get_magma())
    upfloor = get_magma()[int(math.ceil(curr_temp_index))] if math.ceil(curr_temp_index) < len(get_magma()) else get_magma()[len(get_magma())-1]
    downfloor = get_magma()[int(math.floor(curr_temp_index))] if math.floor(curr_temp_index) < len(get_magma()) else get_magma()[len(get_magma())-1]
    mixed = upfloor
    # mixed = colorcvt.oklch_to_linear_srgb(mixed)
    # return vec3i(int(mixed.x*255), int(mixed.y*255), int(mixed.z*255))
    x = mixed[0]*255
    y = mixed[1]*255
    z = mixed[2]*255
    return vec3i(int(x), int(y), int(z))

def gaussian_filter(x: float) -> float:
    return math.exp(-x*x/2) / math.sqrt(2 * math.pi)

def gaussian_interpolation(input: array2d[int], output_w: int, output_h: int) -> array2d[int]:
    input_w = input.n_rows
    input_h = input.n_cols
    assert output_h > input_h and output_w > input_w
    output = array2d(output_w, output_h, default=0.0)
    anchor = array2d(output_w, output_h, default = False)
    scale_w = output_w / input_w
    scale_h = output_h / input_h
    for y in range(input_h):
        for x in range(input_w):
            scaled_pos = vec2i(int(x * scale_w), int(y * scale_h))
            output[scaled_pos] = input[vec2i(x, y)]
            anchor[scaled_pos] = True
    #TODO        
    return output

def linear_interpolation(input: array2d[int], output_w: int, output_h: int) -> array2d[int]:
    input_w = input.n_rows
    input_h = input.n_cols
    assert output_h > input_h and output_w > input_w
    output = array2d(output_w, output_h, default=0)
    anchor = array2d(output_w, output_h, default = False)
    scale_w = output_w / input_w
    scale_h = output_h / input_h
    for y in range(input_h):
        for x in range(input_w):
            scaled_pos = vec2i(int(x * scale_w), int(y * scale_h))
            output[scaled_pos] = input[vec2i(x, y)]
            anchor[scaled_pos] = True
    kernel = array2d.fromlist([
        [290, 480, 290],
        [480, 800, 480],
        [290, 480, 290]
    ])      
    times = int(max(scale_w, scale_h)*0.9)
    for _ in range(times):
        output = output.convolve(kernel, 0)
        output.apply_(lambda x: x//1600)
        for y in range(input_h):
            for x in range(input_w):
                scaled_pos = vec2i(int(x * scale_w), int(y * scale_h))
                output[scaled_pos] = input[vec2i(x, y)]
    return output


heat_map_10x10 = array2d(10, 10, default=10)
# heat_map_10x10.apply_(lambda x: random.randint(10, 10))
#set 3 heat source
heat_map_10x10[vec2i(2, 2)] = heat_map_10x10[vec2i(7,7)] = heat_map_10x10[vec2i(7,2)] = 100
for y in range(heat_map_10x10.n_cols):
    for x in range(heat_map_10x10.n_rows):
        print(f'{heat_map_10x10[vec2i(x, y)]:3}', end='')
    print()
print()
hm_20x20 = linear_interpolation(heat_map_10x10, 40, 40)
for y in range(hm_20x20.n_cols):
    for x in range(hm_20x20.n_rows):
        print(f'{hm_20x20[vec2i(x, y)]:3}', end='')
    print()
hm_20x20.apply_(lambda x: temp_map_srgb(0, 100, x))
for y in range(hm_20x20.n_cols):
    for x in range(hm_20x20.n_rows):
        print(ansi_bg(hm_20x20[vec2i(x, y)], '  '), end='')
    print()