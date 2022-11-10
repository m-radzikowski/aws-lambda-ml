import os
from datetime import datetime
from io import BytesIO
from timeit import default_timer as timer

import boto3
from PIL import Image
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import S3Model
from aws_lambda_powertools.utilities.typing import LambdaContext
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer

logger = Logger()
tracer = Tracer()

s3 = boto3.client("s3")

dynamodb = boto3.resource("dynamodb")
captions_table = dynamodb.Table(os.environ["TABLE_NAME"])

logger.debug("Loading models")
models_loading_start = timer()
model = VisionEncoderDecoderModel.from_pretrained("./vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("./vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("./vit-gpt2-image-captioning")
models_loading_end = timer()
logger.debug("Models loaded", extra={"seconds": round(models_loading_end - models_loading_start, 2)})


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@event_parser(model=S3Model)
def handler(event: S3Model, _: LambdaContext) -> None:
    bucket = event.Records[0].s3.bucket.name
    key = event.Records[0].s3.object.key

    image = load_image(bucket, key)

    caption = generate_caption(image)
    logger.info(f"Caption: {caption}")

    persist_caption(key, caption)


@tracer.capture_method(capture_response=False)
def load_image(bucket: str, key: str) -> Image:
    logger.debug("Loading image")

    file_byte_string = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    image = Image.open(BytesIO(file_byte_string))

    if image.mode != "RGB":
        image = image.convert(mode="RGB")

    return image


@tracer.capture_method(capture_response=False)
def generate_caption(image: Image) -> str:
    logger.debug("Generating caption")

    pixel_values = feature_extractor(images=[image], return_tensors="pt").pixel_values

    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)

    return tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()


@tracer.capture_method(capture_response=False)
def persist_caption(key: str, caption: str) -> None:
    captions_table.put_item(Item={
        "key": key,
        "caption": caption,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
