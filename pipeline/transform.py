"""
The transform step has two main steps:
1. Prepare new data to be loaded into big query. 
2. Construct PinkedIn post.

TODO: Using Chat GPT to make more engaging posts.

Constructs the message to be sent to be posted on my profile.
"""


from datetime import datetime
from typing   import List, Tuple, Dict


########################################################################
# COMPONENT #1: PREPARING DATA FOR BIG QUERY
########################################################################


def prepare_data_for_big_query(problem_solved: Tuple[str, str]) -> Dict:
    """
    INPUT: A single solved problem in the form: (problem, difficulty)
    Example:
    ("Two Sum", "Easy")

    OUTPUT: A dictionary which represents a single row in BQ. 
    Example:
    {
        "problem": "Two Sum", "difficulty": "Easy",
        "url": "https://leetcode.com/problems/two-sum", 
        "date": "2023-06-01",
        "weekday": "Thursday",
    }

    Data must be put into a JSON format in order to be loaded into BQ. The
    keys of the dictionary match the names of the columns in the BQ table.

    Link to BQ table:
    https://console.cloud.google.com/bigquery?project=linkedin-pipeline&ws=
    !1m5!1m4!4m3!1slinkedin-pipeline!2sLEETCODE!3sLEETCODE
    """
    # The problem and difficulty are all the data required to make a post.
    problem, difficulty = problem_solved

    # Date is extracted in SQL format.
    date    = f"{datetime.now().date().strftime('%Y-%m-%d')}"

    # Week day is added, starting with capital letter.
    weekday = f"{datetime.now().date().strftime('%A')}"

    # URL is created from problem name.
    http = "https://leetcode.com/problems"
    url = f'{http}/{problem.lower().replace(" ", "-")}'

    # Result is used to fill big query table.
    result  = {
        "problem":    problem,
        "difficulty": difficulty,
        "url":        url,
        "date":       date,
        "weekday":    weekday
    }

    return result


#########################################################################
# COMPONENT #2: CHECKING FOR NEW PROBLEMS NOT YET POSTED
#########################################################################


def check_for_new_problems(
        leetcode_problems: List[Tuple[str, str]], # input: current problems
        bq_problems:       List[Tuple[str, str]]  # input: old problems
        ) ->               List[Tuple[str, str]]: # output: new problems

    """
    Compares problems from leetcode, to problems in big query, then returns 
    a list of tuples containing there name and difficulty.
    [("Palindrome", "Easy"), ... , ("Two Sum", "Easy")]
    """
    new_problems = []

    # Iterate over the leet code problems.
    for lc_problem in leetcode_problems:

        # If there is a leetcode problem that is not present in BQ,
        if lc_problem not in bq_problems:

            # Add the leetcode problem to a list which will be loaded
            # into BQ.
            new_problems.append(prepare_data_for_big_query(lc_problem))

    return new_problems


#########################################################################
# COMPONENT #3: CONSTRUCT LINKED IN POST
#########################################################################


def construct_linked_in_post(
        list_of_new_solved_problems: List[dict], 
        num_problems_solved: int
        ) -> str:
    
    """
    Creates the linked in post for my profile. If no new problems solved, 
    this function will not be called.
    
    EXAMPLE OUTPUT:
    --------------------------------------------------------------------
    Hello! I recently completed the following Leetcode problem(s):


        ✅ Problem: Reverse Only Letters
        Difficulty: Easy
        URL: https://leetcode.com/problems/reverse-only-letters
        Completed: Friday, 2023-06-02
        

        ✅ Problem: Relative Ranks
        Difficulty: Easy
        URL: https://leetcode.com/problems/relative-ranks
        Completed: Friday, 2023-06-02
    

    Total number of problems solved: 102

    #1000hoursofML #machinelearningengineer #ml #python #mlops
    --------------------------------------------------------------------
    """

    # Intro line.
    message = "Hello! I recently completed the following Leetcode problem(s):"
    message += "\n\n"

    # Adding new solved problems to the post. This is a loop which creates
    # 4 new lines for each new problem.
    message += "\n".join([
    f"""
    ✅ Problem: {dct["problem"]}
    Difficulty: {(dct["difficulty"])}
    URL: {dct["url"]}
    Completed: {dct["weekday"]}, {dct["date"]}
    """ for dct in list_of_new_solved_problems
    ])

    # Summary of total number of problems solved so far.
    message += f"\n\nTotal number of problems solved: {num_problems_solved}"

    # TODO: ADD GPT TEXT

    # Make special notes for when milestones are achieved: 100, 200, 300 etc.
    if num_problems_solved % 100 == 0 and num_problems_solved:
         message += f"""
         \n\n⭐ Milestone achieved: solved {num_problems_solved} problems!
         """

    # Adding hashtags.
    message += """
    \n\n#1000hoursofML #machinelearningengineer #ml #python #mlops\n
    """

    return message


########################################################################
# TRANSFORM DATA
########################################################################


def transform(current_problems, old_problems):
    """Transform data."""

    # 1. Compute number of new problems solved.
    num_problems_solved: int  = len(current_problems)

    # 2. Create list of dictionaries, used to fill rows in BQ.
    new_problems: List = check_for_new_problems(
        current_problems, 
        old_problems
        )

    # 3. Construct the post for LinkedIn.
    linked_in_message: str = construct_linked_in_post(
        new_problems, 
        num_problems_solved
        )

    return new_problems, linked_in_message


def main():
    """For testing."""
    return


if __name__ == "__main__":
    main()

