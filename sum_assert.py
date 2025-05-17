import math

assert_sum = []
anssum = 0
origin_anssum = 0
with open('sum.txt', 'r') as f:
    line = f.read()
    assert_sum.extend([float(num) for num in line.split('\r\n')])
    
tosum = [math.sin(i) for i in range(5000)] + [math.cos(i) for i in range(5000, 9999)]
for i in range(9999):
    try:
        origin_anssum = anssum
        anssum += tosum[i]
        assert anssum == assert_sum[i]
    except AssertionError:
        print(f'on {i}: {origin_anssum} + {tosum[i]} = {anssum}, != {assert_sum[i]}\n')
        exit()