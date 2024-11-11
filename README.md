# Bot Metadata Recorder

This project implements a bot system to record meetings across platforms `Teams`, `Zoom` and `Meets`. The solution leverages AWS Lambda and Fargate to scale as needed.

## Implementation

## Test Coverage

### AWS Lambda Test Coverage

Below are the test coverage results generated on 2024-11-10 19:59 -0300 using `coverage.py v7.2.7`.

| Module                                   | Statements | Missing | Excluded | Coverage |
|------------------------------------------|------------|---------|----------|----------|
| `lambda_test\test_trigger_aws_lambda.py` | 64         | 1       | 0        | 98%      |
| `lambda_trigger\__init__.py`             | 2          | 0       | 0        | 100%     |
| `lambda_trigger\trigger_aws_lambda.py`   | 45         | 0       | 0        | 100%     |
| **Total**                                | 111        | 1       | 0        | 99%      |

#### Details

- **Cobertura Total**: 99%
- The full HTML report can be viewed at [`htmlcov/index.html`](trigger_aws_lambda/htmlcov/index.html).

#### Viewing the Coverage Report

For a detailed analysis of code coverage, you can open the generated HTML report. It is located at `trigger_aws_lambda/htmlcov/index.html` and can be opened in any browser.

### AWS Fargate Test Coverage

#### Details

#### Viewing the Coverage Report