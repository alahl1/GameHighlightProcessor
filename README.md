# FantasyLeague
Using containers to create a fantasy sports platform with AWS microservices.

# Prerequisites
Before running the scripts, ensure you have the following:

(1) Rapidapi.com account, will be needed to access highlight images and videos.

For this example we will be using NCAA (USA College Basketball) highlights since it's included for free in the basic plan.

(2) Verify prerequites are installed
Docker should be pre-installed in most regions
docker --version

AWS CloudShell has AWS CLI pre-installed
aws --version

Python3 should be pre-installed also
python3 --version


(3) AWS Permissions to create resources
I'll provide steps to do this from the UI (AWS Console) and from the CLI (Command Line Interface)

AWS Console
Once logged into AWS console, search "IAM" in the top and click on the name.

In the IAM dashboard you will click on "Users" to the right under Acess Management.
Then click the orange "Create User" button to the right of the page.
Name the user highlights

For the permission options select "Add user to group"
Then click Create a group

Search for the following roles:
AdministratorAccess
ecsTaskExecutionRole

Click on the box beside the role, name the group something you will remember.
Click create group

Under the user groups section, select the group you recently created
Click next
Click create user

CLI/Bash
Attach the AmazonECSTaskExecutionRolePolicy to the IAM User
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

Grant iam:PassRole Permissions To Your User
aws iam put-user-policy \
  --user-name highlights \
  --policy-name AllowPassRoleForECS \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iam:PassRole",
        "Resource": "arn:aws:iam::<your_account_id>:role/ecsTaskExecutionRole"
      }
    ]
  }'

  Prepare the ECS Task Definition
  -This will define how the container will run, CPU/Memory, Networking, and logging

  From the AWS Cloudshell Console(the button beside the serach bar at the top).
  Type "nano task-definition.json"
  Paste the following code into the file after removing <your_account_id> and replacing it with yours.
  {
  "family": "highlight-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "highlight-processor",
      "image": "<your_account_id>.dkr.ecr.us-east-1.amazonaws.com/highlight-processor:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/highlight-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::<your_account_id>:role/ecsTaskExecutionRole"
}

Save the file (control x on mac), press y to save it and enter to confirm the file name

In the CLI type aws ecs register-task-definition --cli-input-json file://task-definition.json

Create CloudWatch Log Group
aws logs create-log-group --log-group-name /ecs/highlight-task

# START HERE 
# Step 1: Open CloudShell Console
Go to aws.amazon.com & sign into your account

In the top, next to the search bar you will see a square with a >_ inside, click this to open the CloudShell

# Step 2: Set Up Your Project
Create the Project Directory
mkdir game-highlight-processor
cd game-highlight-processor

Create the Necessary Files
touch Dockerfile fetch.py requirements.txt

Add code to the files
In the CLI enter nano fetch.py
In another browser navigate to the GitHub Repo and copy the contents within fetch.py


