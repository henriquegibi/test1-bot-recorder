import os

os.environ['S3_BUCKET_NAME'] = 'test-bucket'
os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:region:account-id:test-topic'
os.environ['PROVIDER'] = 'zoom'
os.environ['MEETING_ID'] = '123-456-789'
os.environ['HOST_ACCESS_TOKEN'] = 'example_host_access_token'
