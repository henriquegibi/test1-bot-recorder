# Bot Meeting Recorder

This project implements a bot system to record meetings across platforms `Teams`, `Zoom` and `Meets`. The solution leverages AWS Lambda and Fargate to scale as needed.

## Architecture
<img src="https://github.com/SUMO-Scheduler/bot-recorder/blob/main/images/aws-bot-recorder-drawio.png" alt="AWS Architecture" style="max-width: 100%; height: auto; justify-content: center">

## Implementation
- A CI/CD pipeline would be great, but it is not available at this moment
  - due this, some steps must be done manually
- Whenever you want to update the AWS Lambda, you must _zip_ a new `lambda_handler.py` file and upload it to the S3 Bucket:
  - arn for 795464530711 AWS Account: [arn:aws:s3:::bot-recorder-assets-sumo](https://us-east-1.console.aws.amazon.com/s3/buckets/bot-recorder-assets-sumo)
    - Bucket versioning is disable, since we have this repository to version it
  - within this step, the [Cloudformation](bot_recorder_deploy_iac.yaml) file will be able to deploy the lambda automatically
    - update the IaC file if S3 bucket's ARN changes - for example if deploied in another account.
    - ACL is enable just in case, and bucket has the policy:
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "AllowAccountWideAccess",
          "Effect": "Allow",
          "Principal": {
            "AWS": "arn:aws:iam::795464530711:root"
          },
          "Action": "s3:*",
          "Resource": [
            "arn:aws:s3:::bot-recorder-asset-sumo",
            "arn:aws:s3:::bot-recorder-asset-sumo/*"
          ]
        },
        {
          "Sid": "AllowCloudFormationGetObject",
          "Effect": "Allow",
          "Principal": {
            "Service": "cloudformation.amazonaws.com"
          },
          "Action": "s3:GetObject",
          "Resource": "arn:aws:s3:::bot-recorder-asset-sumo/*"
        }
      ]
    }
    ```

- The deploy will be performed with an EC2 previously configurated, as the ASG instances
  - An AMI file has been created with the [User Data](script\userdata.sh) file.

### Procedure to implement

- Use the [YAML](bot_recorder_deploy_iac.yaml) file to deploy after those intructions above

#### If you need to deploy in other account:

- Download the AMI file
- Download the [AMI Creation](script\create_ami_from_local_image.sh) script
- Make sure both are at the same folder
- Make sure you have AWS CLI running properly
- At file/script folder, run those command below on terminal:
```bash
chmod +x create_ami_from_local_image.sh
./create_ami_from_local_image.sh
```


## Test Coverage

### AWS Lambda Test Coverage

Below are the test coverage results generated on 2024-11-17 22:45 -0300 using `coverage.py v7.2.7`.

| Module                                       | Statements | Missing | Excluded | Coverage |
|----------------------------------------------|------------|---------|----------|----------|
| `test_lambda_handler\test_lambda_handler.py` | 45         | 5       | 0        | 89%      |
| `lambda_handler\lambda_handler.py`           | 42         | 1       | 0        | 98%      |
| **Total**                                    | 87         | 6       | 0        | 93%      |

#### Details

- **Total Coverage**: 99%
- The full HTML report can be viewed at [`htmlcov/index.html`](lambda_handler\htmlcov\index.html).

#### Viewing the Coverage Report

For a detailed analysis of code coverage, you can open the generated HTML report. It is located at `lambda_handler\htmlcov\index.html` and can be opened in any browser.

### AWS Bot Recorder Test Coverage

Below are the test coverage results generated on 2024-11-17 22:45 -0300 using `coverage.py v7.2.7`.

| Module                         | Statements | Missing | Excluded | Coverage |
|--------------------------------|------------|---------|----------|----------|
| `test_app_bot\test_app_bot.py` | 75         | 1       | 0        | 99%      |
| `app_bot\app_bot.py`           | 96         | 33      | 0        | 66%      |
| **Total**                      | 87         | 6       | 0        | 80%      |

#### Details

- **Total Coverage**: 99%
- The full HTML report can be viewed at [`htmlcov/index.html`](app_bot\htmlcov\index.html).

#### Viewing the Coverage Report

For a detailed analysis of code coverage, you can open the generated HTML report. It is located at `app_bot\htmlcov\index.html` and can be opened in any browser.

## Budget Estimate

| Component        | Price per year in USD |
|------------------|-----------------------|
| 2x EC2 m5.xlarge | $ 770.88              |
| **Total**        | $ 770.88              |

#### Considering:
- Purchased 2x _m5.xlarge_ EC2 instance under Computer Saving Plan **all upfront** payment option (for 3 years) for budget optimization
- 