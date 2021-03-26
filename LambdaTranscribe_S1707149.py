import json
import boto3

##Lambda Function
def lambda_handler(event, context):
    
    ##Variables
    c = boto3.client('s3')
    bucket = 'bucket-s1707149'
    
    res = c.list_buckets()
    s3contents = [x['Name'] for x in res['Buckets']]
    
    ##Checks if bucket already exists
    if bucket in s3contents:
        print("Bucket exists")
        
        fname = (event['Records'][0]['body'])
        
        c = boto3.client('transcribe')
        object_url = 'https://s3.amazonaws.com/{0}/{1}'.format(bucket, fname)
        
        res = c.start_transcription_job(TranscriptionJobName= fname, LanguageCode='en-GB', MediaFormat='mp3',
            Media={
                'MediaFileUri': object_url
            }
        )
        
        print(res)    
        print("Execution Success")
    else:
        print("Bucket not found")

    return {
        'statusCode': 200,
        'body': json.dumps('Success from Lambda!')
    }
