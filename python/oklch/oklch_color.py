import math
from linalg import vec3

# Rounds using the typical rule of [x.0, x.5) -> x; [x.5, x+1) -> x+1
def _round(f: float) -> float:
    return 1 if f > 1 else f


class RGB():
    def __init__(self, rgb_vec: vec3) -> None:
        assert rgb_vec.x >= 0 and rgb_vec.y >= 0 and rgb_vec.z >= 0
        if rgb_vec.x > 1 or rgb_vec.y > 1 or rgb_vec.z > 1:
            rgb = rgb_vec.normalize()
        else:
            rgb = rgb_vec
        self._r = rgb.x
        self._g = rgb.y
        self._b = rgb.z
    def __str__(self) -> str:
        return f"RGB({self._r}, {self._g}, {self._b})"
    def to_RGB(self) -> 'RGB':
        return self
    
    @staticmethod
    def _srgb_transfer_function(x: float) -> float:
        if x <= 0.0031308:
            return 12.92 * x
        else:
            return 1.055 * math.pow(x, 1.0 / 2.4) - 0.055
    
    @staticmethod
    def _srgb_transfer_function_inv(x: float) -> float:
        if x <= 0.04045:
            return x / 12.92
        else:
            return math.pow((x + 0.055) / 1.055, 2.4)
    
    def to_OKLAB(self) -> 'OKLAB':
        l = 0.4122214708 * self._srgb_transfer_function_inv(self._r) \
                + 0.5363325363 * self._srgb_transfer_function_inv(self._g) \
                + 0.0514459929 * self._srgb_transfer_function_inv(self._b)
        m = 0.2119034982 * self._srgb_transfer_function_inv(self._r) \
                + 0.6806995451 * self._srgb_transfer_function_inv(self._g) \
                + 0.1073969566 * self._srgb_transfer_function_inv(self._b)
        s = 0.0883024619 * self._srgb_transfer_function_inv(self._r) \
                + 0.2817188376 * self._srgb_transfer_function_inv(self._g) \
                + 0.6299787005 * self._srgb_transfer_function_inv(self._b)

        l_ = math.pow(l, 1/3)
        m_ = math.pow(m, 1/3)
        s_ = math.pow(s, 1/3)

        oklab_vec = vec3(
            0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)
        return OKLAB(oklab_vec)
    
    def to_OKLCH(self) -> 'OKLCH':
        return self.to_OKLAB().to_OKLCH()

        
class OKLAB():
    def __init__(self, oklab_vec: vec3) -> None:
        self._l = oklab_vec.x
        self._a = oklab_vec.y
        self._b = oklab_vec.z
    def __str__(self):
        return f"OKLAB({self._l}, {self._a}, {self._b})"
    
    def to_RGB(self) -> 'RGB':
        l_ = self._l + 0.3963377774 * self._a + 0.2158037573 * self._b
        m_ = self._l - 0.1055613458 * self._a - 0.0638541728 * self._b
        s_ = self._l - 0.0894841775 * self._a - 1.2914855480 * self._b
        
        l = l_ * l_ * l_
        m = m_ * m_ * m_
        s = s_ * s_ * s_
        
        rgb_vec = vec3(
            _round(RGB._srgb_transfer_function(4.0767416621 * l \
                    - 3.3077115913 * m \
                    + 0.2309699292 * s)),
            _round(RGB._srgb_transfer_function(-1.2684380046 * l \
                    + 2.6097574011 * m \
                    - 0.3413193965 * s)),
            _round(RGB._srgb_transfer_function(-0.0041960863 * l \
                    - 0.7034186147 * m \
                    + 1.7076147010 * s)))
        return RGB(rgb_vec)
    
    def to_OKLAB(self) -> 'OKLAB':
        return self
    
    def to_OKLCH(self) -> 'OKLCH':
        c = math.pow(self._a ** 2 + self._b ** 2, 0.5)
        h = math.degrees(math.atan2(self._b, self._a))
        if h < 0:
            h += 360
            
        return OKLCH(vec3(self._l, c, h))


class OKLCH():
    def __init__(self, oklch_vec: vec3) -> None:
        self._l = oklch_vec.x
        self._c = oklch_vec.y
        self._h = oklch_vec.z
    def __str__(self):
        return f"OKLCH({self._l}, {self._c}, {self._h})"
    
    def to_RGB(self) -> 'RGB':
        return self.to_OKLAB().to_RGB()
    
    def to_OKLAB(self) -> 'OKLAB':
        a = math.cos(math.radians(self._h)) * self._c
        b = math.sin(math.radians(self._h)) * self._c
        return OKLAB(vec3(self._l, a, b))
    
    def to_OKLCH(self) -> 'OKLCH':
        return self