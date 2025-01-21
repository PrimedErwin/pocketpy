# 导入 requests 包
import requests

# 发送请求
# x = requests.post('http://127.0.0.1:8080', data = 'Hello!', timeout=5)
x = requests.get('http://127.0.0.1:8080')

# 返回网页内容
print(x.status_code, x.text)