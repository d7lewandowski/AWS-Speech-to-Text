import json
import logging
import boto3
import datetime
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# boto3 - s3 Client
s3 = boto3.client('s3')

# outputfile path and name
output_key = 'Speech-to-Text/output/transcribe_response.json'


def lambda_handler(event, context):
    """
    Function gets the S3 attributes from the tigger event, 
    then invokes the transcribe api to analyze audio files asynchronously
    """

    logger.info(event)

    for record in event['Records']:

        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        # AWS Transcribe client

        transcribe = boto3.client('transcribe')

        # Using datetome to create unique job name
        now = datetime.datetime.now()
        job_uri = f's3://{bucket}/{key}'
        job_name = f'transcribe_job_{now:%Y-%m-%d-%H-%M}'

        # Transcribe audio file

        try:
            response = transcribe.start_transcription_job(      # You are using start_transcription_job asynchronous API
                            TranscriptionJobName=job_name,
                            Media={'MediaFileUri': job_uri},
                            MediaFormat='mp3', # There are several media formats supported.
                            LanguageCode='en-US',                    # The language code for the language used in the input media file.
                            OutputBucketName=bucket,
                            OutputKey=f'Speech-to-Text/output/{job_name}.json',
                        )
            logger.info(response)
            return_result = {'Status': f'Success - The transcribe job: {job_name} has successfully started'}

            # Respone file will be written in the S3 bucket output folder
            # Using S3 clinet to upload the respone file
            s3.put_object(
                Bucket=bucket,
                key=output_key,
                Body=json.dumps(response, default=string_converter)
            )

            return return_result
        except Exception as error:
            print(error)
            return {'Status': 'Failed', "Reason": json.dumps(error, default=str)}


# Function to convert datetime to string.
def string_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()



"""
You can use the code below to create a test event.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<Your_bucket_name>"
                    },
                    "object": {
                    "key": "input/sample_transcribe_1.mp3"
                    }
                }
                }
            ]
}
"""