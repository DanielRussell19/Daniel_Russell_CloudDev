## Daniel Russell S1707149 CPD
import boto3

##Create S3 From Boto3
try:
    c = boto3.client('s3')
    res = c.list_buckets()
    
    s3contents = [x['Name'] for x in res['Buckets']]
    
    if 'bucket-s1707149' in s3contents:
        print("Bucket already exists")
    else:
        c.create_bucket(
            Bucket='bucket-s1707149',
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
        )   
except Exception as e:
    print("Error: S3 Create")
    print(e)

##Create SQS From Boto3 
try:
    c = boto3.resource('sqs')
    #q = c.get_queue_by_name(QueueName='que-s1707149')
    
    #q = c.create_queue(QueueName='que-s1707149', Attributes={'DelaySeconds': '30'})
    
except Exception as e:
    print("Error: SQS Create")
    print(e)

##Create DynamoTable From Template using CloudFormation
#try:
   # c = boto3.client('cloudformation')
    
#except Exception as e:
   # print("Error: Cloud Formation")
   # print(e)

##Upload audiofiles in 30sec intervals to S3 Bucket??
#try:
    #s3 = boto3.client('s3')
    #filename = 'file.txt'
    #bucket_name = 'my-bucket'
    #s3.upload_file(filename, bucket_name, filename)
    
#except Exception as e:
   # print("Error: Audio File Upload")
   # print(e)

##Upload must send message to SQS to trigger Lambda fucntion??
#try:
   # c = boto3.resource('sqs')
   # 
#except Exception as e:
   # print("Error: Upload Message")
   # print(e)

##NOTES to be deleted
##AMAZON Console Stuff --
##Lambda in console must extract from SQS message before sending to transcribe

##Transcribe in console
##must call back to lambda and 
##sent to comprehend

##call back to lambda function
##extract from comprehend and save results in
##table for positive, negative and mixed score

##Negitive scores trigger an SMS message 
##to telephone