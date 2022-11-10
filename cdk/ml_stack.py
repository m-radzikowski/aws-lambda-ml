from aws_cdk import Stack, RemovalPolicy, Duration
from aws_cdk.aws_dynamodb import Table, BillingMode, Attribute, AttributeType
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Tracing
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.aws_s3 import Bucket, EventType
from aws_cdk.aws_s3_notifications import LambdaDestination
from constructs import Construct


class MLStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        captions_table = Table(
            self, "CaptionsTable",
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=BillingMode.PAY_PER_REQUEST,
            partition_key=Attribute(name="key", type=AttributeType.STRING),
        )

        captioning_lambda = DockerImageFunction(
            self, "CaptioningLambda",
            code=DockerImageCode.from_image_asset("./captioning_lambda/"),
            memory_size=10 * 1024,
            timeout=Duration.minutes(5),
            reserved_concurrent_executions=1,
            tracing=Tracing.ACTIVE,
            log_retention=RetentionDays.ONE_MONTH,
            environment={
                "LOG_LEVEL": "DEBUG",
                "POWERTOOLS_SERVICE_NAME": "captioning",
                "TABLE_NAME": captions_table.table_name,
            }
        )

        captions_table.grant_write_data(captioning_lambda)

        images_bucket = Bucket(
            self, "ImagesBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        images_bucket.add_event_notification(EventType.OBJECT_CREATED, LambdaDestination(captioning_lambda))
        images_bucket.grant_read(captioning_lambda)
