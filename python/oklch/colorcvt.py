import math
from linalg import vec3

def _round(f: float) -> float:
    return 1 if f > 1 else f

def _lrgb_to_oklab(lrgb: vec3) -> vec3:
    assert lrgb.x >= 0 and lrgb.y >= 0 and lrgb.z >= 0
    if lrgb.x > 1 or lrgb.y > 1 or lrgb.z > 1:
        _lrgb = lrgb.normalize()
    else:
        _lrgb = lrgb
        
    l = vec3(0.4122214708, 0.5363325363, 0.0514459929).dot(_lrgb)
    m = vec3(0.2119034982, 0.6806995451, 0.1073969566).dot(_lrgb)
    s = vec3(0.0883024619, 0.2817188376, 0.6299787005).dot(_lrgb)
    
    l_ = math.pow(l, 1/3)
    m_ = math.pow(m, 1/3)
    s_ = math.pow(s, 1/3)
    lms_ = vec3(l_, m_, s_)
    
    return vec3(
        vec3(0.2104542553, 0.7936177850, -0.0040720468).dot(lms_),
        vec3(1.9779984951, -2.4285922050, 0.4505937099).dot(lms_),
        vec3(0.0259040371, 0.7827717662, -0.8086757660).dot(lms_))
    
def _oklab_to_lrgb(oklab: vec3) -> vec3:
    l_ = vec3(1, 0.3963377774, 0.2158037573).dot(oklab)
    m_ = vec3(1, -0.1055613458, -0.0638541728).dot(oklab)
    s_ = vec3(1, -0.0894841775, -1.2914855480).dot(oklab)
    
    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_
    lms = vec3(l, m, s)
    
    return vec3(
        _round(vec3(4.0767416621, -3.3077115913, 0.2309699292).dot(lms)),
        _round(vec3(-1.2684380046, 2.6097574011, -0.3413193965).dot(lms)),
        _round(vec3(-0.0041960863, 0.0415873371, 4.2860173251).dot(lms)))
    
def _oklab_to_oklch(oklab: vec3) -> vec3:
    c = math.pow(oklab.y ** 2 + oklab.z ** 2, 0.5)
    h = math.degrees(math.atan2(oklab.z, oklab.y))
    if h < 0:
        h += 360
    return vec3(oklab.x, c, h)

def _oklch_to_oklab(oklch: vec3) -> vec3:
    a = math.cos(math.radians(oklch.z)) * oklch.y
    b = math.sin(math.radians(oklch.z)) * oklch.y
    return vec3(oklch.x, a, b)

def lrgb_to_oklch(lrgb: vec3) -> vec3:
    return _oklab_to_oklch(_lrgb_to_oklab(lrgb))

def oklch_to_lrgb(oklch: vec3) -> vec3:
    return _oklab_to_lrgb(_oklch_to_oklab(oklch))

__all__ = ['lrgb_to_oklch', 'oklch_to_lrgb']