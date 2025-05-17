import math

assert_sum = []
anssum = 0
origin_anssum = 0
with open('basic_op.txt', 'r') as f:
    line = f.read()
    assert_sum.extend([float(num) for num in line.split('\r\n')])
    
tosum = assert_sum[:99999]
assert_sum = assert_sum[99999:]

for i in range(99999):
    try:
        origin_anssum = anssum
        anssum += tosum[i]
        assert anssum == assert_sum[i]
    except AssertionError:
        print(f'on {i}: {origin_anssum} + {tosum[i]} = {anssum}, != {assert_sum[i]}\n')
