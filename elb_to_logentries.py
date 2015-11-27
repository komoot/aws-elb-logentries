#!/usr/bin/env python

import socket
import boto3
import csv
import json
s3_client = boto3.resource('s3')

with open("tokens.json", 'r') as f:
    tokens = json.load(f)

def find_token(key):
    """Finds the appropriate token for the key (filename)"""
    filename = key.split('/')[-1]
    for prefix, t in tokens.items():
        if filename.startswith(prefix):
            return t
    raise ValueError("No token found for " + key)


def lambda_handler(event, context):
    """AWS lambda entry point"""
    for record in event['Records']:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3_out(record['s3']['bucket']['name'], record['s3']['object']['key'])

def s3_out(bucket, key, token=None, dummy=False):
    """Download s3 file and output to logentries"""
    if not token:
        token = find_token(key)
    if dummy:
        s = Dummy()
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect(('data.logentries.com', 80))	
    object = s3_client.Object(bucket, key)
    body = object.get()["Body"].read()
    rows = csv.reader(body.splitlines(), delimiter=' ', quotechar='"')
    for line in rows:
        # timestamp elb client:port backend:port request_processing_time backend_processing_time response_processing_time elb_status_code backend_status_code received_bytes sent_bytes "request" "user_agent" ssl_cipher ssl_protocol
        # 2015-11-17T09:08:10.792842Z main-api-live 188.77.4.65:55891 10.0.1.27:80 0.000049 0.039685 0.00003 200 200 0 601 "GET https://api.komoot.de:443/v006/user_highlights/86208?fields=geometry%2Chighlighters%2Cimages%2CratingCounter%2CmidPoint&hl=de&srid=4326&usersetting.creator.username=43149878736 HTTP/1.1" "de.komoot.berlinbikeapp/7.2 iPhone OS/9.1 (de-DE) (iPhone)" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2
        if len(line) > 12:
            request = line[11].split(' ')
            idx = request[1].find('/', 9)
            url = request[1][idx:]
            parsed = {
                'ip': line[2].split(':')[0],
                'method': request[0],
                'url': url,
                'user_agent': line[12]
                }
            msg = "{0} ip={ip} t={5} es={7} bs={8} ib={9} ob={10} m={method} {url} \"{user_agent}\"\n".format(*line, **parsed)
            s.send(token + msg)
        else:
            s.send(token + "ERROR line too short: " + ' '.join(line) + "\n")
    s.close()  

class Dummy:
    def connect(self, dummy):
        pass
    def send(self, data):
        print(data),
    def close(self):
        pass

# test execution
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Import s3 logs to logentries')
    parser.add_argument('-t', dest='token', required=False, help='logentries token')
    parser.add_argument('bucket', help='s3 bucket name')
    parser.add_argument('key', help='s3 key')
    args = parser.parse_args()
    s3_out(args.bucket, args.key, args.token, dummy=True)
    
