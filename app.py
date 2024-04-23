from flask import Flask, request, send_file
import boto3
import os
from io import BytesIO

app = Flask(__name__)


AWS_BUCKET_NAME = 'tll-sidecar-poc-bucket'
AWS_REGION = 'us-east-1'

s3_client = boto3.client('s3', region_name=AWS_REGION)


@app.route('/health-check', methods=['GET'])
def health_check():
    return "ready", 200


@app.route('/get-file', methods=['GET'])
def get_file():
    # Example path: /myfolder/mysubfolder/myfile.txt
    file_path = request.args.get('path')

    if not file_path:
        return "File path parameter 'path' is missing.", 400

    s3_key = file_path.strip('/')

    try:
        # Fetching the file from S3
        response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
        file_content = response["Body"].read()

        # Create a byte stream to send the file
        file_stream = BytesIO(file_content)
        file_stream.seek(0)

        # Inferring the file type and filename from the path
        file_name = os.path.basename(file_path)
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/octet-stream',
        )
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)
