"""
Creates post on linkedin.
"""

# pylint: disable=E0611:no-name-in-module
import os
import json
from typing  import Dict
from google.cloud import bigquery
import requests
from pipeline.config_files.config import LINKED_IN_OATH_2_TOKEN
from pipeline.config_files.config import LINKED_IN_USER_URN
from pipeline.config_files.config import GCP_CREDENTIALS_JSON_PATH


# Initialize the BigQuery client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDENTIALS_JSON_PATH
client = bigquery.Client.from_service_account_json(GCP_CREDENTIALS_JSON_PATH)
TABLE_ID = 'linkedin-pipeline.LEETCODE.LEETCODE'
print("Service account connected.")


# def insert_row(row):
#     """Func"""
#     # Insert the row into the table
#     errors = client.insert_rows_json(TABLE_ID, [row])
#     if errors:
#         print('Error inserting row:', errors)


########################################################################
# COMPONENT #1: LOAD DATA INTO BQ
########################################################################


def send_data_to_bigquery(row: Dict):
    """Func"""

    query = f"""
    SELECT * FROM `{TABLE_ID}` 
    WHERE problem = "{row["problem"]}"
    """

    result = client.query(query).result()

    row_exists = len(list(result)) > 0

    if not row_exists:
        try:
            client.insert_rows_json(TABLE_ID, [row])
        except Exception as error:
            print('Error inserting row:', error)
    else:
        print('Value already exists in the table')


########################################################################
# COMPONENT #2: POST ON LINKED IN
########################################################################


def create_linkedin_post_through_api(message: str) -> bool:
    """
    Uses requests library to creates linked in post, using my "company" 
    API.
    """

    # This is the api url for making a post.
    # https://learn.microsoft.com/en-us/linkedin/marketing/integrations/
    # community-management/shares/posts-api
    url = 'https://api.linkedin.com/v2/ugcPosts'

    headers = {
        'Authorization': f'Bearer {LINKED_IN_OATH_2_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202305',
        'Content-Type': 'application/json'
    }

    payload = {
        "author": f"urn:li:person:{LINKED_IN_USER_URN}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{message}"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Making request to API.
    response = requests.post(
        url, 
        headers=headers, 
        data=json.dumps(payload), 
        timeout=60
    )
    print(response)
    return True


def main():
    """For testing."""
    return


if __name__ == "__main__":
    main()
