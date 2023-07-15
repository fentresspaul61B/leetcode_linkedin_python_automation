"""Testing suit to validate connection, functionality, and how the pipeline works together."""

# pylint: disable=E0611:no-name-in-module
import unittest
import json
import requests
from pipeline.config_files.config import LINKED_IN_OATH_2_TOKEN
from pipeline.config_files.config import LINKED_IN_USER_URN
from pipeline.extract             import extract



class TestLeetcodeAPI(unittest.TestCase):
    """Validating ability to pull data from Leetcode."""

    def test_return_type_of_leetcode_api_response(self):
        """Expecting a list of responses."""
        leetcode_problems_solved, big_query_problems_solved, big_query_json = extract()
        self.assertTrue(isinstance(leetcode_problems_solved, list))
        self.assertTrue(isinstance(big_query_problems_solved, list))
        self.assertTrue(isinstance(big_query_json, list))
        self.assertTrue(isinstance(big_query_json[0], dict))

    def test_length_of_leetcode_api_response(self):
        """Expecting the list to be greater than 0."""
        leetcode_problems_solved, _, _ = extract()
        self.assertTrue(len(leetcode_problems_solved) > 0)


class TestLinkedInApi(unittest.TestCase):
    """Validating connections to different APIs."""


    def test_linkedin_auth_valid(self):
        """Checks if linkedin token is still valid."""
        auth_token = LINKED_IN_OATH_2_TOKEN
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get("https://api.linkedin.com/v2/me",
                                headers=headers,
                                timeout=60)
        self.assertEqual(response.status_code, 200, "Authentication token is valid.")

        data = response.text
        linkedin_api_response_data = json.loads(data)

        self.assertEqual(LINKED_IN_USER_URN, linkedin_api_response_data["id"])


if __name__ == "__main__":
    unittest.main()
