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
    # test_list = [('Convert an Array Into a 2D Array With Conditions', 'Medium'), ('Left and Right Sum Differences', 'Easy'), ('Take Gifts From the Richest Pile', 'Easy'), ('Count Distinct Numbers on Board', 'Easy'), ('Separate the Digits in an Array', 'Easy'), ('Minimum Common Value', 'Easy'), ('Alternating Digit Sum', 'Easy'), ('Find Consecutive Integers from a Data Stream', 'Medium'), ('Categorize Box According to Criteria', 'Easy'), ('Number of Unique Subjects Taught by Each Teacher', 'Easy'), ('Make Array Zero by Subtracting Equal Amounts', 'Easy'), ('Smallest Number in Infinite Set', 'Medium'), ('Root Equals Sum of Children', 'Easy'), ('Find Closest Number to Zero', 'Easy'), ('K Radius Subarray Averages', 'Medium'), ('Find Target Indices After Sorting Array', 'Easy'), ('Concatenation of Array', 'Easy'), ('Build Array from Permutation', 'Easy'), ('Sign of the Product of an Array', 'Easy'), ('Recyclable and Low Fat Products', 'Easy'), ('Find Total Time Spent by Each Employee', 'Easy'), ('Daily Leads and Partners', 'Easy'), ('Invalid Tweets', 'Easy'), ('Checking Existence of Edge Length Limited Paths', 'Hard'), ('Average Time of Process per Machine', 'Easy'), ('Customer Who Visited but Did Not Make Any Transactions', 'Easy'), ('Design Parking System', 'Easy'), ('Matrix Diagonal Sum', 'Easy'), ('Find Kth Bit in Nth Binary String', 'Medium'), ('Number of Good Pairs', 'Easy'), ('The kth Factor of n', 'Medium'), ('Average Salary Excluding the Minimum and Maximum Salary', 'Easy'), ('Maximum Number of Vowels in a Substring of Given Length', 'Medium'), ('Consecutive Characters', 'Easy'), ('Replace Employee ID With The Unique Identifier', 'Easy'), ('Generate a String With Characters That Have Odd Counts', 'Easy'), ('Maximum 69 Number', 'Easy'), ('Maximum Number of Occurrences of a Substring', 'Medium'), ('Check If It Is a Straight Line', 'Easy'), ('Split a String in Balanced Strings', 'Easy'), ('Minimum Cost to Move Chips to The Same Position', 'Easy'), ('Reformat Department Table', 'Easy'), ('Article Views I', 'Easy'), ('Defanging an IP Address', 'Easy'), ('Game Play Analysis I', 'Easy'), ('Sales Analysis III', 'Easy'), ('Project Employees I', 'Easy'), ('Occurrences After Bigram', 'Easy'), ('Product Sales Analysis I', 'Easy'), ('Actors and Directors Who Cooperated At Least Three Times', 'Easy'), ('Last Stone Weight', 'Easy'), ('Squares of a Sorted Array', 'Easy'), ('Similar String Groups', 'Hard'), ('Palindromic Substrings', 'Medium'), ('Maximum Average Subarray I', 'Easy'), ('Not Boring Movies', 'Easy'), ('Big Countries', 'Easy'), ('Find Customer Referee', 'Easy'), ('Employee Bonus', 'Easy'), ('Keyboard Row', 'Easy'), ('Construct the Rectangle', 'Easy'), ('Max Consecutive Ones', 'Easy'), ('License Key Formatting', 'Easy'), ('Intersection of Two Arrays', 'Easy'), ('Top K Frequent Elements', 'Medium'), ('Bulb Switcher', 'Medium'), ('Add Digits', 'Easy'), ('Binary Tree Paths', 'Easy'), ('Valid Anagram', 'Easy'), ('Product of Array Except Self', 'Medium'), ('Power of Two', 'Easy'), ('Contains Duplicate', 'Easy'), ('Rising Temperature', 'Easy'), ('Customers Who Never Order', 'Easy'), ('Duplicate Emails', 'Easy'), ('Employees Earning More Than Their Managers', 'Easy'), ('Rank Scores', 'Medium'), ('Combine Two Tables', 'Easy'), ('Majority Element', 'Easy'), ('Two Sum II - Input Array Is Sorted', 'Medium'), ('Min Stack', 'Medium'), ('Evaluate Reverse Polish Notation', 'Medium'), ('Longest Consecutive Sequence', 'Medium'), ('Valid Palindrome', 'Easy'), ('Maximum Depth of Binary Tree', 'Easy'), ('Merge Sorted Array', 'Easy'), ('Remove Duplicates from Sorted List', 'Easy'), ('Spiral Matrix II', 'Medium'), ('Maximum Subarray', 'Medium'), ('Group Anagrams', 'Medium'), ('Valid Sudoku', 'Medium'), ('Search Insert Position', 'Easy'), ('Merge Two Sorted Lists', 'Easy'), ('Valid Parentheses', 'Easy'), ('Longest Common Prefix', 'Easy'), ('Roman to Integer', 'Easy'), ('Container With Most Water', 'Medium'), ('Palindrome Number', 'Easy'), ('Zigzag Conversion', 'Medium'), ('Two Sum', 'Easy')]
    # test_rows = prepare_data_for_big_query(test_list)
    # print(check_value_exists({'problem': 'Zigzag Conversion', 'difficulty': 'Medium', 'url': 'https://leetcode.com/problems/zigzag-conversion', 'date': '2023-06-01'}))
    # test_list = [('Convert an Array Into a 2D Array With Conditions', 'Medium'), ('Left and Right Sum Differences', 'Easy'), ('Take Gifts From the Richest Pile', 'Easy'), ('Count Distinct Numbers on Board', 'Easy'), ('Separate the Digits in an Array', 'Easy'), ('Minimum Common Value', 'Easy'), ('Alternating Digit Sum', 'Easy'), ('Find Consecutive Integers from a Data Stream', 'Medium'), ('Categorize Box According to Criteria', 'Easy'), ('Number of Unique Subjects Taught by Each Teacher', 'Easy'), ('Make Array Zero by Subtracting Equal Amounts', 'Easy'), ('Smallest Number in Infinite Set', 'Medium'), ('Root Equals Sum of Children', 'Easy'), ('Find Closest Number to Zero', 'Easy'), ('K Radius Subarray Averages', 'Medium'), ('Find Target Indices After Sorting Array', 'Easy'), ('Concatenation of Array', 'Easy'), ('Build Array from Permutation', 'Easy'), ('Sign of the Product of an Array', 'Easy'), ('Recyclable and Low Fat Products', 'Easy'), ('Find Total Time Spent by Each Employee', 'Easy'), ('Daily Leads and Partners', 'Easy'), ('Invalid Tweets', 'Easy'), ('Checking Existence of Edge Length Limited Paths', 'Hard'), ('Average Time of Process per Machine', 'Easy'), ('Customer Who Visited but Did Not Make Any Transactions', 'Easy'), ('Design Parking System', 'Easy'), ('Matrix Diagonal Sum', 'Easy'), ('Find Kth Bit in Nth Binary String', 'Medium'), ('Number of Good Pairs', 'Easy'), ('The kth Factor of n', 'Medium'), ('Average Salary Excluding the Minimum and Maximum Salary', 'Easy'), ('Maximum Number of Vowels in a Substring of Given Length', 'Medium'), ('Consecutive Characters', 'Easy'), ('Replace Employee ID With The Unique Identifier', 'Easy'), ('Generate a String With Characters That Have Odd Counts', 'Easy'), ('Maximum 69 Number', 'Easy'), ('Maximum Number of Occurrences of a Substring', 'Medium'), ('Check If It Is a Straight Line', 'Easy'), ('Split a String in Balanced Strings', 'Easy'), ('Minimum Cost to Move Chips to The Same Position', 'Easy'), ('Reformat Department Table', 'Easy'), ('Article Views I', 'Easy'), ('Defanging an IP Address', 'Easy'), ('Game Play Analysis I', 'Easy'), ('Sales Analysis III', 'Easy'), ('Project Employees I', 'Easy'), ('Occurrences After Bigram', 'Easy'), ('Product Sales Analysis I', 'Easy'), ('Actors and Directors Who Cooperated At Least Three Times', 'Easy'), ('Last Stone Weight', 'Easy'), ('Squares of a Sorted Array', 'Easy'), ('Similar String Groups', 'Hard'), ('Palindromic Substrings', 'Medium'), ('Maximum Average Subarray I', 'Easy'), ('Not Boring Movies', 'Easy'), ('Big Countries', 'Easy'), ('Find Customer Referee', 'Easy'), ('Employee Bonus', 'Easy'), ('Keyboard Row', 'Easy'), ('Construct the Rectangle', 'Easy'), ('Max Consecutive Ones', 'Easy'), ('License Key Formatting', 'Easy'), ('Intersection of Two Arrays', 'Easy'), ('Top K Frequent Elements', 'Medium'), ('Bulb Switcher', 'Medium'), ('Add Digits', 'Easy'), ('Binary Tree Paths', 'Easy'), ('Valid Anagram', 'Easy'), ('Product of Array Except Self', 'Medium'), ('Power of Two', 'Easy'), ('Contains Duplicate', 'Easy'), ('Rising Temperature', 'Easy'), ('Customers Who Never Order', 'Easy'), ('Duplicate Emails', 'Easy'), ('Employees Earning More Than Their Managers', 'Easy'), ('Rank Scores', 'Medium'), ('Combine Two Tables', 'Easy'), ('Majority Element', 'Easy'), ('Two Sum II - Input Array Is Sorted', 'Medium'), ('Min Stack', 'Medium'), ('Evaluate Reverse Polish Notation', 'Medium'), ('Longest Consecutive Sequence', 'Medium'), ('Valid Palindrome', 'Easy'), ('Maximum Depth of Binary Tree', 'Easy'), ('Merge Sorted Array', 'Easy'), ('Remove Duplicates from Sorted List', 'Easy'), ('Spiral Matrix II', 'Medium'), ('Maximum Subarray', 'Medium'), ('Group Anagrams', 'Medium'), ('Valid Sudoku', 'Medium'), ('Search Insert Position', 'Easy'), ('Merge Two Sorted Lists', 'Easy'), ('Valid Parentheses', 'Easy'), ('Longest Common Prefix', 'Easy'), ('Roman to Integer', 'Easy'), ('Container With Most Water', 'Medium'), ('Palindrome Number', 'Easy'), ('Zigzag Conversion', 'Medium'), ('Two Sum', 'Easy')]
    # new_rows = prepare_data_for_big_query(test_list)
    # create_linkedin_post_through_api(".")
    return


if __name__ == "__main__":
    main()
