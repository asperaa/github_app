#!flask/bin/python
from flask import Flask, make_response, jsonify, request, abort
import json
import requests
import time
import logging

#Create and configure logger 
logging.basicConfig(filename="github_app_file.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG) 

# github API token
token = '432151f03f311773d4311c2ec7c48cb81ede76ef'

app = Flask(__name__)

def github_repo_call(org_id):
    """Calls the Github API to get all the repositories
       of the organisation based on organisation id

       Args:
           org_id (int): The id of the organisation
       
       Returns:
           JSON: The return value.
           Example: [
                        {"name":"rick", "stars": 100},
                        {"name":"morty", "stars": 98},
                        {"name":"jerry", "stars":2}
                    ]
               
    """
    # header and url to make the gtihub API call
    headers = {'Authorization': 'token '+token}
    url = 'https://api.github.com/orgs/'+str(org_id)+'/repos'
    
    # making the API GET request using the url and headers
    params = {'per_page': 100}
    response = requests.get(url, params, headers=headers)

    if response.status_code != 200:
        return {"results": "Some error occured. Please try again with correct org spelling"}
    
    num_pages = 1
    LOGGER.debug(response.headers)

    if 'Link' in response.headers:
        last_header_part = response.headers['Link'][-15:]
    
        if last_header_part[0] == '=':
            num_pages = int(last_header_part[1])
        else:
            num_pages = int(last_header_part[:2])
        # print(num_pages)

    
    # stores essential info like name and stars for all the repos
    final_list = []
    
    # dictionary to store the sorted repos on the basis of stars
    sort_dict = {}
    
    # iterate through each repository and store name and star count
    # then sort on the basis of star count
    mega_list_repos = []
    
    for page in range(1, num_pages + 1):
        params={'page': page}
        LOGGER.debug("----Page number:--------")
        LOGGER.debug(page)
        page_response = requests.get(url, params, headers=headers)
        for each_repo in page_response.json():
            mega_list_repos.append(each_repo)
    
    
    
    LOGGER.debug("-------------------------Number of repos-------------------------")
    LOGGER.debug(len(mega_list_repos))
    LOGGER.debug("----------------------------------End of Number of repos-----------------------")
    
    for repo in mega_list_repos:
        repo_info = {}
        repo_info["name"] = repo["name"] if "name" in repo else None
        repo_info["stars"] = repo["stargazers_count"] if "stargazers_count" in repo else None
        sort_dict[repo_info["name"]] = repo_info["stars"]
        final_list.append(repo_info)
    
    # sorting the repos on the basis of star count
    sorted_x = sorted(sort_dict.items(), key=lambda kv: kv[1])    
    top_three_repos = []
    
    LOGGER.debug("--------------- Sorted list of repos on basis of github stars--------------")
    LOGGER.debug(sorted_x)
    LOGGER.debug("---------------- End of sorted list --------------")

    # selecting the top three repos
    if len(sorted_x) >= 3:
        counter = 0
        for x in reversed(sorted_x):
            counter += 1
            repo_info = {}
            repo_info["name"] = x[0]
            repo_info["stars"] = x[1]
            top_three_repos.append(repo_info)
            if counter == 3:
                break
    else:
        for x in reversed(sorted_x):
            repo_info = {}
            repo_info["name"] = x[0]
            repo_info["stars"] = x[1]
            top_three_repos.append(repo_info)
        
    result = {"results": top_three_repos}
    
    LOGGER.debug("-----------------Final Results of top 3 repos-----------------------")
    LOGGER.debug(result)
    LOGGER.debug("------------------End of Final top 3 repos---------------------")

    return result

@app.route('/repos', methods=['POST'])
def get_top_repos():
    """Calls the funtion to make the Github API call
       to get the repositories of an organsiation

       GET:
           Summary: repos endpoint.
           Description: Get the top 3 repositories of an org.
           Parameters:
               - org: organisation_id
           Responses:
               200:
                   Description: Json object to be returned (list of dictionaries)
                   Schema: Repos Schema
                           {
                            "results": [
                                        {"name":"rick", "stars": 100},
                                        {"name":"morty", "stars": 98},
                                        {"name":"jerry", "stars":2},
                                       ]
                           }
        
    """
    # lambda function to get the current time
    current_milli_time = lambda: int(round(time.time() * 1000))
    
    # store the time before the API call
    pre_request = current_milli_time()
    
    LOGGER.debug("Pre-request time stamp")
    LOGGER.debug(pre_request)

    # check if the JSON is there or if required key is there in JSON
    if not request.json or not 'org' in request.json:
        abort(400)
    
    # make the Github API call to get the top 3 repositories of an org
    top_repos = github_repo_call(request.json['org'])
    
    # store the time after the API response is received
    post_response = current_milli_time()

    # calculate the diffrence between the pre-request
    # and post-reponse time
    response_time = (post_response - pre_request)/1000
    
    LOGGER.debug("----------- Post response time stamp--------------")
    LOGGER.debug(post_response)

    # print the reponse time on the console
    print("The response time of repos endpoint (in seconds):", response_time)
    
    return json.dumps(top_repos)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
