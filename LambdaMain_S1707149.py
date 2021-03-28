## Daniel Russell S1707149 CPD

##Imports
import json
import boto3
import time
import urllib.request

##Global Variables
number = '+4407903899757'
bucket = 'bucket-s1707149'
table = 'Table-S1707149'

##Function for SMS texting via SNS Publish
def sms(fname, scoring, result):
    try:
        ##sends message correcting negative sentiment via sms text message
        c = boto3.client('sns')
        c.publish(PhoneNumber = number, Message='Stop being so negative. ' + fname + ' ' + scoring + ' ' + result)
    except Exception as e:
        print("SNS Function Failed " + fname)
        print(e)
        return "SNSFailed"

##Function for Inserting AudioName and Scoring into Database
def dynamo(fname, scoring):
    try:
        ##puts the audio name and scoring into dynamodb
        c = boto3.client('dynamodb')
        c.put_item(TableName= table, Item= { 'AudioName': {'S': fname}, 'AudioScoring': {'S': scoring} })
    except Exception as e:
        print("Table Function Failed " + fname)
        print(e)
        return "TableFailed"

##Function for comprehend, sentiment analysis
def comprehend(result):
    try:
        ##takes result and passes it through comprehend
        ##the resulting senitment is returned
        c = boto3.client('comprehend')
        res = c.detect_sentiment(Text= result,LanguageCode='en')['Sentiment']
        return res
        
    except Exception as e:
        print("Comprehend Function Failed " + result)
        print(e)
        return "CompFailed"

##Function for speech to text transcribing
def transcribe(fname, objurl):
    try:
        ##gets list of completed transciption jobs that are complete and have the same name
        c = boto3.client('transcribe')
        
        try:
            res = c.list_transcription_jobs(Status= 'COMPLETED', JobNameContains= fname)['TranscriptionJobSummaries'][0]['TranscriptionJobName']
        except Exception:
            res = 'null'
        
        ##checks if the transciption already exists else the job is created and retrived 30secs post request
        ##path to transcription is returned
        if res == fname:
            res = c.get_transcription_job(TranscriptionJobName= fname)
            print("Previous Job Found " + fname)
            
            transpath = res['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return transpath
        else:
            c.start_transcription_job(TranscriptionJobName= fname, LanguageCode='en-GB', MediaFormat='mp3',Media={'MediaFileUri': objurl})
            print("New Job Created " + fname)
            time.sleep(30)
            
            res = c.get_transcription_job(TranscriptionJobName= fname)
            transpath = res['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return transpath
    except Exception as e:
        print("Transcribe Function Failed " + fname)
        print(e)
        return "TranscribeFailed"

##Lambda Function Starting Point
def lambda_handler(event, context):
    
    try:
        c = boto3.client('s3')
        
        ##Get list of buckets
        res = c.list_buckets()
        s3contents = [x['Name'] for x in res['Buckets']]
        
        ##Checks if bucket already exists
        if bucket in s3contents:
            print("Bucket exists")
            
            ##get file name from sqs message
            fname = (event['Records'][0]['body'])
            
            ##creates a url to the audio file present in bucket
            object_url = 'https://s3.amazonaws.com/{0}/{1}'.format(bucket, fname)
            
            ##filename and url is sent to function transcribe, url of transcription is returned
            out = transcribe(fname, object_url)
            
            if out != "TranscribeFailed":
                ##gets transption from url
                content = urllib.request.urlopen(out).read().decode('UTF-8')
            
                ##loads the content into json and prossessed into desired result, only the transription
                data =  json.loads(content)
                result = data['results']['transcripts'][0]['transcript']
                
                ##transcription is passed to comprehend for analysis, score is return
                scoring = comprehend(result)
                
                if scoring != "CompFailed":
                    ##file name and score are passed to dynamodb for storage
                    dynamo(fname, scoring)
                    
                    if scoring == 'NEGATIVE':
                        sms(fname, scoring, result)
                        print("End!")
                        return {'statusCode': 200,'body': json.dumps('Success from Lambda!')}
                    else:
                        print("End!")
                        return {'statusCode': 200,'body': json.dumps('Success from Lambda!')}
        else:
            print("Bucket not found")
            return {'statusCode': 404,'body': json.dumps('Failure from Lambda!')}
        
        print("Transcribe/Comprehend Failed. " + fname)
        return {'statusCode': 400,'body': json.dumps('Failure from Lambda!')}
    except Exception as e:
        print(e)
        return {'statusCode': 400,'body': json.dumps('Failure from Lambda!')}
    
