## Daniel Russell S1707149 CPD
import boto3
import time

##Variables
bucket = 'bucket-s1707149'
sqs = 'que-s1707149'
stack = 'stack-s1707149'

templatedir = './Templates/DynamoDB_S1707149CPD.template'
audiodirs = ['./Files/Audio1.mp3', './Files/Audio2.mp3', './Files/Audio3.mp3', './Files/Audio4.mp3', './Files/Audio5.mp3']

#Shortened dirs for debugging
#audiodirs = ['./Files/Audio1.mp3']

sqsurl = 'https://sqs.eu-west-2.amazonaws.com/335830697146/que-s1707149'

##Create S3 From Boto3
try:
    c = boto3.client('s3')
    
    ##retrives bucket instances
    res = c.list_buckets()
    s3contents = [x['Name'] for x in res['Buckets']]
    
    ##Checks if bucket already exists/Create new bucket
    if bucket in s3contents:
        print("Bucket already exists")
    else:
        c.create_bucket(
            Bucket= bucket,
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
        )
        print("Bucket Created")
        
except Exception as e:
    print("Error: S3 ERROR")
    print(e)


##Create SQS From Boto3 
try:
    c = boto3.resource('sqs')
    
    ##Checks if queue exists
    q = c.get_queue_by_name(QueueName= sqs)
    print("Queue Found")
    
except Exception as e:
    ##if error attempts to create the queue
    q = c.create_queue(QueueName= sqs, Attributes={'DelaySeconds': '30'})
    print(e)
    print("SQS Created")
    
except Exception as e:
    print("Error: SQS ERROR")
    print(e)


##Create DynamoTable From Template using CloudFormation
try:
   c = boto3.client('cloudformation')
   
   ##checks if stack exists/creates new stack
   stackcontents = c.list_stacks()['StackSummaries']
   if stack in stackcontents:
       print("Stack exists")
   else:
       templatefile = open(templatedir)
       templatebody = templatefile.read()
       
       #validate template
       c.validate_template(TemplateBody= templatebody)
       
       ##create stack
       res = c.create_stack(StackName= stack,TemplateBody= templatebody)
       print("Stack Created, Table Created")
except Exception as e:
   print("Error: Cloud Formation")
   print(e)

##Upload audiofiles in 30sec intervals to S3 Bucket
try:
    c = boto3.client('s3')
    q = boto3.client('sqs')
    i = 1

    for x in audiodirs:
        c.upload_file(x, bucket, 'Audio' + str(i))
        print('Audio' + str(i) + ' :Uploaded')
        
        res = q.send_message(QueueUrl= sqsurl, MessageBody= 'Audio' + str(i), DelaySeconds= 30)
        print('Audio' + str(i) + ' :SQS Sent for Lambda Trigger')
        time.sleep(10)
        i = i + 1
    
except Exception as e:
    print("Error: Audio File Upload")
    print(e)
    
print("End of execution.")