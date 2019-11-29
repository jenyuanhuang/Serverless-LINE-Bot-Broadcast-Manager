# Serverless LINE Bot Broadcast Manager
Administrators can control their own offical LINE Bot by personal LINE account, and send many different types of broadcast messages to their followers. 

## How it works?
We use AWS [Lambda](https://aws.amazon.com/tw/lambda/) and [API Gateway](https://aws.amazon.com/tw/api-gateway/) to build our serverless framework.

Create an AWS Lambda function and upload the entire project to it. 

Add LINE_ADMIN_USER_ID, LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET to the environment variables.

![](https://i.imgur.com/qAro1XG.png)