from flask import Flask,request,make_response,jsonify
from jsonschema import ValidationError
import io
import datetime
import os
import rembg
import png
from rembg import remove
from PIL import Image
import requests
from flask_expects_json import expects_json
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv, dotenv_values

# ...
app = Flask(__name__)
load_dotenv()
validation = {
    "type": "object",
    "properties": {
        "url":{"type":"string"}
    },
    "required": ["url"]
}
def upload_to_aws(image, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_ID'),
                      aws_secret_access_key=os.getenv('AWS_ACCESS_KEY'))
    try:
        img = io.BytesIO()
        image.save(img, 'PNG')
        img.seek(0)
        s3.upload_fileobj(img,os.getenv("AWS_BUCKET_NAME"), s3_file)
        print("Upload Successful")
        link = 'https://testi.exponentialhost.com/' + s3_file
        return link
        # return 'https:i.exponentialhost.com/textInImage/image.png'
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False 
 
     
@app.route('/background',methods=['POST'])
@expects_json(validation)
def IMG():
        try: 
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
                url=json['url']
                #url = "https://tse4.explicit.bing.net/th?id=OIP.Q7U_BhI3XQYtCkuwPlFNRwHaE8&pid=Api&P=0"
                print(url)
                    # logo = Image.open(url)
                img = Image.open(requests.get(url, stream=True).raw)
                output=remove(img)
                presentDate = datetime.datetime.now()
                unix_timestamp = datetime.datetime.timestamp(presentDate)*1000  
                link=upload_to_aws(output,'background/' + str(int(unix_timestamp)) + '.png')
                return{
                'url':link
                }
                output_path = 'output2.png' 
                print(output)
                output.save(output_path)
                return "working"
            else:
                return "content type not supported"
        except Exception as e:
            print
            return {"message":"something went wrong"}

@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({'error': original_error.message}), 400)
    # handle other "Bad Request"-errors
    return error

if __name__ == "__main__":
    app.run(debug=True)
