import requests

with open('dummy1.pdf', 'wb') as f:
    f.write(b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n')

url = 'http://localhost:8000/api/v1/pdf/compress/'
files = {'file': open('dummy1.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.status_code)
print(response.json())
