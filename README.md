# Serverless Machine Learning pipeline

Example Machine Learning model running on AWS Lambda.

The pipeline consists of S3 bucket, Lambda function, and DynamoDB table.
On image upload to the bucket, Lambda function generates image caption
and puts it in the table.

See the article with full description:
[Running Serverless ML on AWS Lambda](https://betterdev.blog/serverless-ml-on-aws-lambda/)

## Requirements

This project uses [pyenv](https://github.com/pyenv/pyenv)
and [Poetry](https://python-poetry.org/).
Install them and set

```bash
poetry config virtualenvs.prefer-active-python true
```

for seamless experience.

It also requires [CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) installed.

## Development

Install dependencies:

```bash
poetry install
```

Activate virtual environment:

```bash
poetry shell
```

Deploy:

```bash
cdk deploy
```

## Sample images

Sample images are from [Pexels](https://www.pexels.com/).
