#!/bin/bash

name="send_elb_access_logs_to_logentries"
zip="$(pwd)/build.zip~"

echo "creating zip file ${zip}"
zip ${zip} elb_to_logentries.py tokens.json

if [ "x$1" == "xcreate" ]; then
  echo "creating function '${name}'"
	aws lambda create-function --function-name ${name} \
			--role arn:aws:iam::963797398573:role/lambda_s3_read \
			--handler elb_to_logentries.lambda_handler \
			--timeout 10 \
			--memory-size 128 \
			--zip-file "fileb://${zip}" \
			--runtime python2.7
else
  echo "updating function '${name}'"
	aws lambda update-function-code --function-name ${name} --zip-file "fileb://${zip}"
fi


rm ${zip}
