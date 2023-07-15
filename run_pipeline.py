"""
Connects the extract, transform and load steps into a single pipeline.
Runs pipeline on schedule to check for new solved problems, every 3 
hours, and make LI post. This pipeline is automatically triggered using 
github actions.
"""

# Run pipeline on schedule to check for new solved problems, every night,
# And make LI post. This pipeline is automatically triggered using github
# actions.

# pylint: disable=E0611:no-name-in-module
from pipeline.extract   import extract
from pipeline.transform import transform
from pipeline.load      import create_linkedin_post_through_api
from pipeline.load      import send_data_to_bigquery


def run_pipeline():
    """
    Tests pipeline:
    Does everything except post to linkedIN.
    """

    # 1. Extract all data.
    try:
        leetcode_problems_solved, big_query_problems_solved = extract()
    except Exception as error:
        print("Extraction failed.")
        print(error)
        return None

    # 2. Transform
    try:
        new_problems, linked_in_message = transform(
            leetcode_problems_solved,
            big_query_problems_solved
            )
    except Exception as error:
        print("Transform failed.")
        print(error)
        return None

    # 3. load data into linkedin and into big query.
    print(linked_in_message)
    condition_1 = len(new_problems) > 1 and len(leetcode_problems_solved) > 1
    condition_2 = (condition_1 and len(leetcode_problems_solved) % 100 == 0)
    if condition_1 or condition_2:

        # Post message to LinkedIn.
        # print(linked_in_message)
        create_linkedin_post_through_api(linked_in_message)

        # Update pickle file for data backup.
        for problem in new_problems:
            send_data_to_bigquery(problem)


def main():
    run_pipeline()

if __name__ == "__main__":
    main()
