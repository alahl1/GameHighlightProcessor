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
AmazonEC2ContainerRegistryFullAccess

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
Reminder to replace with your S3bucket name, your RapidAPI key and region
Exit and Save file

In CLI enter nano Dockerfile
Paste the code found within the Dockerfile on Github into the blank area
Exit and Save file

In CLI enter nano requirements.txt
Paste the code found within the requirements.txt file on Github into the blank area
Exit and Save file

# Step 3: Build and Test the Docker Container
Build the Docker Image
docker build -t highlight-processor .

Run the Docker Image Locally
docker run highlight-processor

Verify that the script fetches highlights and stores them in your specified S3 bucket

# Troubleshooting Step 3 Errors SKIP IF SUCCESSFUL
If you get the error message "Unable to locate credentials", this is typically because your script that is running in the Docker container, cannot access your AWS credentials. We need to pass the AWS credentials into the container.

(1) Verfiy AWS Credntials Locally
aws configure

Provide your "Access Key ID", "Secret Access Key" and Region. The Access Key ID can be found in IAM under "Users" and the Secret Acces Key is provided when you created the User. If you didn't copy this value you will have to create a new user with the proper permissions and update this info. See prereq in ReadME for help.

Check the credentials are valid
aws s3 ls
If this works, then your credntials are correct

(2) Pass AWS Credentials to Docker
Find your AWS credntials file location
cat ~/.aws/credentials

Run the Docker container and bind the AWS credentials directory
docker run -v ~/.aws:/root/.aws highlight-processor

this will mount your local .aws directory inside the contianer and make your credntials available to the boto3 client.

# Step 4: Push the Docker Image to Amazon Elastic Container Registry (ECR)
Create an ECR Repository
aws ecr create-repository --repository-name highlight-processor

Authenticate Docker with ECR
Replace <your_account_id> with your account id
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your_account_id>.dkr.ecr.us-east-1.amazonaws.com

Tag and Push the image
Replace <your_account_id> with your account id
docker tag highlight-processor:latest <your_account_id>.dkr.ecr.us-east-1.amazonaws.com/highlight-processor:latest
docker push <your_account_id>.dkr.ecr.us-east-1.amazonaws.com/highlight-processor:latest

# Troubleshooting Step 4 Errors SKIP IF SUCCESSFUL
Confirm you've added the appropriate permissions to interact with Amazon ECR
From the IAM Console, select Users from the left hand menu
Select the User or role associated with the credentials you are using
Attach a policy, click add permissions, attach policies directly
Search and add this managed policy "AmazonEC2ContainerRegistryFullAccess"

# Step 5: Set Up AWS Fargate to Run the Script
Create an ECS Cluster
aws ecs create-cluster --cluster-name highlight-cluster

Register the task
aws ecs register-task-definition --cli-input-json file://task-definition.json

Run the Task
