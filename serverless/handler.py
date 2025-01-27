import os
import logging
import json

from utils import get_spreadsheet_data, upload_to_s3, get_filename_from_key

log = logging.getLogger()
log.setLevel(os.environ["LOG_LEVEL"])


def run(event, _):
    log.info(f"Received input event: {json.dumps(event, default=str)}")

    SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
    BUCKET_NAME = os.environ["BUCKET_NAME"]
    BUCKET_KEY = os.environ["BUCKET_KEY"]

    output_filename = get_filename_from_key(BUCKET_KEY)
    content = get_spreadsheet_data(SPREADSHEET_ID)
    response = upload_to_s3(bucket=BUCKET_NAME, key=BUCKET_KEY, data=content)
    if response:
        log.info(f"Successfully uploaded {output_filename} to S3")
    else:
        log.info(f"Failed to upload {output_filename} to S3")
