import requests 
import base64
import json

#task send image to be saved to s3 inside a folder

#image_file = open("myphoto.jpg", "rb")
with open("myphoto.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

response = requests.post('https://w1vz8j0cqk.execute-api.us-east-1.amazonaws.com/prod/demo-lambda',json={'name':'bahh.jpg','file':encoded_string.decode()})
print(response.json())