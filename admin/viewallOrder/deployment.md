sam build -t template.yaml
sam package --output-template-file packaged.yaml --s3-bucket ration-pro-qa
sam deploy --template-file packaged.yaml --region ap-south-1 --capabilities CAPABILITY_IAM --stack-name viewallOrder