import json
import boto3
import time
import urllib.request

##Global Variables
number = '+4407903899757'
bucket = 'bucket-s1707149'
table = 'Table-S1707149'

def sms():
    try:
        c = boto3.client('sns')
        c.publish(PhoneNumber = number, Message='You have been a naughty naughty boy. Stop being so negative.' )
    except Exception as e:
        print("SNS Function Failed")
        print(e)
        return "SNSFailed"

def dynamo(fname, scoring):
    try:
        c = boto3.client('dynamodb')
        c.put_item(TableName= table, Item= { 'AudioName': {'S': fname}, 'AudioScoring': {'S': scoring} })
    except Exception as e:
        print("Table Function Failed")
        print(e)
        return "TableFailed"

def comprehend(result):
    try:
        c = boto3.client('comprehend')
        res = c.detect_sentiment(Text= result,LanguageCode='en')['Sentiment']
        return res
        
    except Exception as e:
        print("Comprehend Function Failed")
        print(e)
        return "CompFailed"

def transcribe(fname, objurl):
    try:
        c = boto3.client('transcribe')
        res = c.list_transcription_jobs(Status= 'COMPLETED', JobNameContains= fname)['TranscriptionJobSummaries'][0]['TranscriptionJobName']
        
        if res == fname:
            res = c.get_transcription_job(TranscriptionJobName= fname)
            print("Previous Job Found")
            
            transpath = res['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return transpath
        else:
            c.start_transcription_job(TranscriptionJobName= fname, LanguageCode='en-GB', MediaFormat='mp3',Media={'MediaFileUri': objurl})
            print("New Job Created")
            time.sleep(30)
            
            res = c.get_transcription_job(TranscriptionJobName= fname)
            transpath = res['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return transpath
    except Exception as e:
        print("Transcribe Function Failed")
        print(e)
        return "TranscribeFailed"

##Lambda Function Start Point
def lambda_handler(event, context):
    
    try:
        ##Variables
        c = boto3.client('s3')
        
        res = c.list_buckets()
        s3contents = [x['Name'] for x in res['Buckets']]
        
        ##Checks if bucket already exists
        if bucket in s3contents:
            print("Bucket exists")
            
            fname = (event['Records'][0]['body'])
            object_url = 'https://s3.amazonaws.com/{0}/{1}'.format(bucket, fname)
            
            out = transcribe(fname, object_url)
            
            if out != "TranscribeFailed":
                content = urllib.request.urlopen(out).read().decode('UTF-8')
            
                data =  json.loads(content)
                result = data['results']['transcripts'][0]['transcript']
                
                scoring = comprehend(result)
                
                if scoring != "CompFailed":
                    dynamo(fname, scoring)
                    
                    if scoring == 'NEGATIVE':
                        sms()
                        print("End!")
                        return {'statusCode': 200,'body': json.dumps('Success from Lambda!')}
                    else:
                        print("End!")
                        return {'statusCode': 200,'body': json.dumps('Success from Lambda!')}
        else:
            print("Bucket not found")
            return {'statusCode': 404,'body': json.dumps('Failure from Lambda!')}
        
        print("Transcribe/Comprehend Failed.")
        return {'statusCode': 400,'body': json.dumps('Failure from Lambda!')}
    except Exception as e:
        print(e)
        return {'statusCode': 400,'body': json.dumps('Failure from Lambda!')}
    
