import requests
import json
text = requests.get(url='http://127.0.0.1:8000/api/policies').text

data = json.loads(text)

print(data[0])