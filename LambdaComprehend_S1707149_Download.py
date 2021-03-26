import json
import boto3

##Variables
c = boto3.client('s3')
bucket = 'bucket-s1707149'

##Lambda Function
def lambda_handler(event, context):
    
    res = c.list_buckets()
    s3contents = [x['Name'] for x in res['Buckets']]
    
    ##Checks if bucket already exists
    if bucket in s3contents:
        print("Bucket exists")
            
        print("Execution Success")
    else:
        print("Bucket not found")

    return {
        'statusCode': 200,
        'body': json.dumps('Success from Lambda!')
    }
