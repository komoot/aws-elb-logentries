# aws-elb-logentries
Forwards AWS ELB logs from S3 to logentries via lambda

## Setup
1. Enable access log logging for your ELB in you AWS console.
1. Clone this repository
1.1 Edit the ```tokens.json``` config file. It is a map of filename prefixes and logentries target tokens. Therefore you can have all ELBs log into the same bucket but send each elb log with another token. The key is just the filename prefix.
1. (Optional) Edit the ```deploy.sh``` script and change the name of the lambda function.
1. Run ```bash deploy.sh create``` (Make sure you have ```aws-cli``` installed and your keys set up properly)
1. Go to the lambda console, edit the function configuration and connect the function to the "object created" event in your s3 bucket.

## Update function
If you modified the tokens or the function code, run ```bash deploy.sh``` to update your function.

## Testing
You can test the function on your local machine with ```python elb_to_logentries.py [-t logentries_token] mybucket path/to/access/log```
