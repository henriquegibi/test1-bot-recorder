import os

os.environ['TESTING'] = '1'
os.environ['CLUSTER_NAME'] = 'test-cluster'
os.environ['TASK_DEFINITION'] = 'test-task'
os.environ['SUBNET_ID'] = 'subnet-12345678'
os.environ['SECURITY_GROUP_ID'] = 'sg-12345678'
