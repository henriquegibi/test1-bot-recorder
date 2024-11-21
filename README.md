# Bot Meeting Recorder

This project implements a bot system to record meetings across platforms `Teams`, `Zoom` and `Meets`. The solution leverages AWS Lambda and Fargate to scale as needed.

## Architecture
![AWS Architecture](images\aws-bot-recorder-drawio.png)

## Implementation
- A CI/CD pipeline would be great, but it is not available at this moment
- Whenever you want to update the AWS Lambda, you must _zip_ the `lambda_handler.py` file and upload it to the S3 Bucket:
  - arn: 
  - within this step, the [Cloudformation](bot_recorder_deploy_iac.yaml) file will be able to deploy the lambda automatically
    - update this file if S3 bucket's ARN changes.

### Procedure to implement

- Download the AMI file
- Download the [AMI Creation](script\create_ami_from_local_image.sh) script
- Make sure both ar at the same folder
- Make sure you have AWS CLI running properly
- At file/script folder, run those command below on terminal:
```
chmod +x create_ami_from_local_image.sh
./create_ami_from_local_image.sh
```
- Use the [YAML](bot_recorder_deploy_iac.yaml) file to deploy after those intructions above

## Test Coverage

### AWS Lambda Test Coverage

Below are the test coverage results generated on 2024-11-17 22:45 -0300 using `coverage.py v7.2.7`.

| Module                                       | Statements | Missing | Excluded | Coverage |
|----------------------------------------------|------------|---------|----------|----------|
| `test_lambda_handler\test_lambda_handler.py` | 45         | 5       | 0        | 89%      |
| `lambda_handler\lambda_handler.py`           | 42         | 1       | 0        |  98%     |
| **Total**                                    | 87         | 6       | 0        | 93%      |

#### Details

- **Total Coverage**: 99%
- The full HTML report can be viewed at [`htmlcov/index.html`](lambda_handler\htmlcov\index.html).

#### Viewing the Coverage Report

For a detailed analysis of code coverage, you can open the generated HTML report. It is located at `lambda_handler\htmlcov\index.html` and can be opened in any browser.

### AWS Bot Recorder Test Coverage

#### Details

#### Viewing the Coverage Report

## Budget Estimate

| Component        | Price per year in USD |
|------------------|-----------------------|
| 2x EC2 m5.xlarge | $ 770.88              |
| **Total**        | $ 770.88              |

#### Considering:
- Purchased 2x _m5.xlarge_ EC2 instance under Computer Saving Plan **all upfront** payment option (for 3 years) for budget optimization
- 