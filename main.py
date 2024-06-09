'''
curl -X 'PUT' \
  'http://5.63.153.31:5051/v1/account/6205bc37-1fd1-4811-bce8-f174f4daf8f6' \
  -H 'accept: text/plain'
}'
'''
import pprint

import requests

# url = 'http://5.63.153.31:5051/v1/account'
# headers = {
#     'accept': '*/*',
#     'Content-Type': 'application/json'
# }
# json = {
#     "login": "naruto_50",
#     "email": "naruto_50@gmail.com",
#     "password": "123456789"
# }
#
# response = requests.post(
#     url=url,
#     headers=headers,
#     json=json
# )

url = 'http://5.63.153.31:5051/v1/account/6205bc37-1fd1-4811-bce8-f174f4daf8f6'
headers = {
    'accept': 'text/plain',
}


response = requests.put(
    url=url,
    headers=headers,
)

print(response.status_code)
pprint.pprint(response.json())
response_json = response.json()
print(response_json['resource']['rating']['quantity'])