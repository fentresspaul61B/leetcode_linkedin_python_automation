"""
TODO
# Makes call to Leetcode API: https://github.com/fspv/python-leetcode
"""

# pylint: disable=E0611:no-name-in-module


from typing import List, Tuple
import os
import leetcode

from google.cloud import bigquery
from pipeline.config_files.config import GCP_CREDENTIALS_JSON_PATH
from pipeline.config_files.config import LEET_CODE_CSRF_AUTH_TOKEN
from pipeline.config_files.config import LEET_CODE_SESSION_AUTH_TOKEN


# Initialize the BigQuery client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDENTIALS_JSON_PATH
BIG_QUERY_CLIENT = bigquery.Client.from_service_account_json(
    GCP_CREDENTIALS_JSON_PATH
    )
TABLE_ID = 'linkedin-pipeline.LEETCODE.LEETCODE'

########################################################################
# COMPONENT #1: EXTRACT (PROBLEM, DIFFICULTY) FROM BQ
########################################################################


def extract_problems_only_from_bq() -> List[Tuple[str, str]]:
    """
    Extracts the solved problems from bq.

    Return object:
    [("Palindrome", "Easy"), ... , ("Two Sum", "Easy")]

    The output of this function is used to compare to the Leetcode list. 
    If the problems in big query match the problems from leetcode, no 
    new problems have been solved, if there are more problems from 
    leetcode, then new problems have been solved.
    """

    # SQL Query to select two columns: (problem, difficulty)
    query = f"SELECT problem, difficulty FROM `{TABLE_ID}`"

    # Execute the SQL command.
    query_result = BIG_QUERY_CLIENT.query(query).result()

    # For each row in the big query result.
    problems = []
    for data in query_result:

        # [(problem, difficulty), ... , (problem, difficulty)]
        problems.append((data[0], data[1]))
    
    return problems


########################################################################
# COMPONENT #2: EXTRACT (PROBLEM, DIFFICULTY) FROM LEETCODE
########################################################################


def extract_leet_code_data_from_api() -> List[Tuple]:
    """
    Extracts the solved problems from leet code.

    Return object:
    [("Palindrome", "Easy"), ... , ("Two Sum", "Easy")]

    The output of this function is used to compare to the big query 
    list. If the problems in leet code match the problems from big 
    query, no new problems have been solved, if there are more problems 
    from leetcode, then new problems have been solved.
    """

    # Setting up API configuration.
    configuration = leetcode.Configuration()
    configuration.api_key["x-csrftoken"] = LEET_CODE_CSRF_AUTH_TOKEN
    configuration.api_key["csrftoken"] = LEET_CODE_CSRF_AUTH_TOKEN
    configuration.api_key["LEETCODE_SESSION"] = LEET_CODE_SESSION_AUTH_TOKEN
    configuration.api_key["Referer"] = "https://leetcode.com"
    configuration.debug = False

    # Creating leetcode API object to make calls.
    api_instance = leetcode.DefaultApi(leetcode.ApiClient(configuration))
    # print(api_instance)

    # Making API request.
    try:
        api_response = api_instance.api_problems_topic_get(topic="all")
    except Exception as error:
        print(error)

    # Iterating through all my solved questions returned from API 
    # request.
    solved_questions = []
    for questions in api_response.stat_status_pairs:
        # print(api_response.stat_status_pairs)
        # print(questions)
        

        # Seeking all of my "accepted" questions, denoted by "ac".
        if questions.status=="ac":

            # Collect the id and title (id is often wrong so not posting
            # in message currently.)
            level = questions.difficulty.level
            difficulty = ""
            if level == 1:
                difficulty = "Easy"
            elif level == 2:
                difficulty = "Medium"
            elif level == 3:
                difficulty = "Hard"

            data = (questions.stat.question__title, difficulty)

            # Add the data to the list of dictionaries.
            solved_questions.append(data)

            # print(len(solved_questions))

    return solved_questions


########################################################################
# EXTRACT DATA
########################################################################


def extract():
    """
    STEP 1:
    Extracts the solved problems from leet code.
    [("Palindrome", "Easy"), ... , ("Two Sum", "Easy")]

    STEP 2:
    Extracts the solved problems from BQ.
    [("Palindrome", "Easy"), ... , ("Two Sum", "Easy")]
    """
    # STEP 1
    leetcode__list = extract_leet_code_data_from_api()
    
    # STEP 2
    big_query_list = extract_problems_only_from_bq()

    assert isinstance(leetcode__list, list)
    assert isinstance(big_query_list, list)
    return leetcode__list, big_query_list



def main():
    print(len(extract_leet_code_data_from_api()))
    print(len(extract_problems_only_from_bq()))
    return


if __name__ == "__main__":
    main()
