import boto3
host = "localhost"
user = "root"
password = "200319792003saa2003"
db_name = "givemepaw"

session = boto3.Session(
        aws_access_key_id='GELVNJU1QH5CFGCSPJLK',
        aws_secret_access_key='ets2ACj0UQDHZs4gWANWddNQVYYfZySVcMA0t78Z'
    )
s3 = session.client(
        service_name='s3',
        endpoint_url='https://obs.ru-moscow-1.hc.sbercloud.ru')
