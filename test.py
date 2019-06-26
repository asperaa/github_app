import unittest
import os
import json
import app
from app import app as apps
import requests

class RepoTestCase(unittest.TestCase):
    """This class represents the Repositories Test Case"""
    
    def setUp(self):
        self.repos1 = app.github_repo_call(450)
        self.repos2 = app.github_repo_call(3)
    
    def tearDown(self):
        pass

    def test_github_repo_call(self):
    
        json_response1 = {
                            "results": [
                                            {"name": "maple.watch", "stars": 6}, 
                                            {"name": "speedrun.com", "stars": 4}, 
                                            {"name": "sumofbest.com", "stars": 0}
                                        ]
                         }
        
        json_response2 = {
                            "results": [
                                            {"name": "pair-box", "stars": 0},
                                            {"name": "dotfiles", "stars": 0}
                                        ]
                         }
        
        self.assertEqual(self.repos1, json_response1)
        self.assertEqual(self.repos2, json_response2)
    
    def test_get_top_repos(self):
        tester = apps.test_client(self)
        response = tester.post('/repos', data={'org': 3})
        # self.assertEqual(response.status_code, 200)

        json_response = {"results": [
                                        {"name": "pair-box", "stars": 0}, 
                                        {"name": "dotfiles", "stars": 0}
                                    ]
                        }

        self.assertEqual(response.data, json_response)


if __name__ == "__main__":
    unittest.main()