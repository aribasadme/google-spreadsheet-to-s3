import logging

import boto3
from botocore.exceptions import ClientError
import gspread

log = logging.getLogger()


def upload_to_s3(bucket: str, key: str, data: list) -> bool:
    """Uploads file into S3 bucket"""
    s3_client = boto3.client('s3')
    csv_content = list_of_lists_to_string(data)
    try:
        response = s3_client.put_object(Bucket=bucket,
                                        Key=key,
                                        Body=csv_content.encode('utf-8'))
        log.debug(response)
    except ClientError as e:
        log.error(e)
        return False
    return True


def get_spreadsheet_data(spreadsheet_id: str) -> list:
    """Downloads spreadsheet data from Google Sheets"""
    log.info(f"Downloading {spreadsheet_id}")
    try:
        client = gspread.service_account(filename="service-account-credentials.json")
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.get_worksheet(0)  # First worksheet
        content = worksheet.get_all_values()  # Get all rows as list of lists
        log.info(f"Downloaded {len(content)} rows from {spreadsheet_id}")
        return content
    except Exception as e:
        log.error(e)
        return []


def get_filename_from_key(key: str) -> str:
    """Extracts filename from S3 key"""
    return key.split("/")[-1]


def list_of_lists_to_string(data: list) -> str:
    """Converts list of lists to CSV string"""
    return "\n".join([",".join(row) for row in data])
