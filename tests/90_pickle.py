import pickle as pkl

def test(data): # type: ignore
    print('-'*50)
    b = pkl.dumps(data)
    print(b)
    o = pkl.loads(b)
    print(o)
    assert data == o

test(None)                      # PKL_NONE
test(1)                         # PKL_INT8
test(277)                       # PKL_INT16
test(-66666)                    # PKL_INT32
test(0xffffffffffff)            # PKL_INT64
test(1.0)                       # PKL_FLOAT32
test(1.12312434234)             # PKL_FLOAT64
test(True)                      # PKL_TRUE
test(False)                     # PKL_FALSE
test("hello")                   # PKL_STRING
test(b"hello")                  # PKL_BYTES

from linalg import vec2, vec3, vec2i, vec3i

test(vec2(2/3, 1.0))            # PKL_VEC2
test(vec3(2/3, 1.0, 3.0))       # PKL_VEC3
test(vec2i(1, 2))               # PKL_VEC2I
test(vec3i(1, 2, 3))            # PKL_VEC3I

test(vec3i)                     # PKL_TYPE

test([1, 2, 3])                 # PKL_LIST
test((1, 2, 3))                 # PKL_TUPLE
test({1: 2, 3: 4})              # PKL_DICT

# test complex data
test([1, '2', True])
test([1, '2', 3.0, True])
test([1, '2', True, {'key': 4}])
test([1, '2', 3.0, True, {'k1': 4, 'k2': [b'xxxx']}])

exit()

from pickle import dumps, loads, _wrap, _unwrap

def test(x):
    y = dumps(x)
    # print(y.decode())
    ok = x == loads(y)
    if not ok:
        _0 = _wrap(x)
        _1 = _unwrap(_0)
        print('='*50)
        print(_0)
        print('-'*50)
        print(_1)
        print('='*50)
        assert False

test(1)
test(1.0)
test("hello")
test(True)
test(False)
test(None)

test([1, 2, 3])
test((1, 2, 3))
test({1: 2, 3: 4})

class Foo:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Foo):
            return False
        return self.x == __value.x and self.y == __value.y
    
    def __repr__(self) -> str:
        return f"Foo({self.x}, {self.y})"
    
test(Foo(1, 2))
test(Foo([1, True], 'c'))

from linalg import vec2

test(vec2(1, 2))

a = {1, 2, 3, 4}
test(a)

a = bytes([1, 2, 3, 4])
test(a)

a = [1, 2]
d = {'k': a, 'j': a}
c = loads(dumps(d))

assert c['k'] is c['j']
assert c == d

# test circular references
from collections import deque

a = deque([1, 2, 3])
test(a)

a = [int, float, Foo]
test(a)