import requests
import json
import argparse
import sys
import datetime

def list_github_repositories(user_or_org, token, num_of_projects):
    """
    Fetches a list of repositories for a specified GitHub user or organization.

    This function performs the following steps:
    1. Sets up the necessary headers for authentication if a token is provided.
    2. Iterates through the paginated results of the GitHub API to fetch repositories.
    3. Collects repositories until the specified number of projects is reached or there are no more repositories.
    4. Parses the response to extract repository names and URLs and stores them in a dictionary.

    Args:
        user_or_org (str): The GitHub username or organization name whose repositories are to be fetched.
        token (str, optional): The GitHub personal access token for authentication. Default is None.
        num_of_projects (int, optional): The maximum number of repositories to fetch. Default is 1000.

    Returns:
        dict: A dictionary where the keys are repository names and the values are dictionaries containing
              repository URLs and names.
              Example:
              {
                  "RepoName1": {"full_url": "https://github.com/user_or_org/RepoName1", "name": "RepoName1"},
                  "RepoName2": {"full_url": "https://github.com/user_or_org/RepoName2", "name": "RepoName2"}
              }

    Raises:
        SystemExit: If there is an error in retrieving repositories from GitHub.
    """
    repo_dict = {}
    headers = {}    
    repos = []

    page = 1
    per_page = 100
    url = f"https://api.github.com/users/{user_or_org}/repos"
   
    if token:
        headers['Authorization'] = f"token {token}"
    
    while len(repos) < num_of_projects:
        response = requests.get(url, headers=headers, params={'per_page': per_page, 'page': page})
        if response.status_code == 200:
            page_repos = response.json()
            repos.extend(page_repos)
            if len(page_repos) < per_page or len(repos) >= num_of_projects:
                # Stop if fewer than `per_page` repos are returned or we've reached the max_repos limit
                break
            page += 1
            
        else:
            print(f"Failed to retrieve repositories: {response.status_code}")
            sys.exit()
            print(response.json())
    
    for repo in repos:
        repo_dict[repo['name']] = {
        'full_url': repo['html_url'],
        'name': repo['name']
        }

    return repo_dict

def list_checkmarx_projects(api_key):
    """
    Fetches a list of Checkmarx projects using an API key.

    This function performs the following steps:
    1. Authenticates with the Checkmarx IAM service using the provided API key (as a refresh token)
       to obtain an access token.
    2. Uses the access token to retrieve a list of projects from the Checkmarx AST API.
    3. Parses the response to extract project names and IDs and stores them in a dictionary.

    Args:
        api_key (str): The API key used to authenticate with the Checkmarx IAM service.

    Returns:
        dict: A dictionary where the keys are project names and the values are dictionaries containing
              project IDs and project names.
              Example:
              {
                  "ProjectName1": {"proj_id": "123", "proj_name": "ProjectName1"},
                  "ProjectName2": {"proj_id": "456", "proj_name": "ProjectName2"}
              }

    Raises:
        SystemExit: If authentication with the Checkmarx IAM service fails.
    """
    url = "https://deu.iam.checkmarx.net/auth/realms/events-canary/protocol/openid-connect/token"
    data = {
        'grant_type': 'refresh_token',
        'client_id': 'ast-app',
        'refresh_token': api_key
    }

    auth_response = requests.post(url, data=data)
    if auth_response.status_code == 200:
        authentication = auth_response.json()
        jwt_token = authentication['access_token']
        
    else:
        print(f"Failed to get authentication: {auth_response.status_code}")
        sys.exit()

    url = "https://deu.ast.checkmarx.net/api/projects/?limit=1000"
    headers = {
        'Accept': 'application/json; version=1.0',
        'Authorization': f'Bearer {jwt_token}'
    }

    proj_response = requests.get(url, headers=headers)

    if proj_response:
        projects = proj_response.json()['projects'];
        proj_dict = {}

        for proj in projects:
            proj_dict[proj['name']] = {
                'proj_id': proj['id'],
                'proj_name': proj['name']
                }

    return proj_dict

def compare_lists(github_repositories, checkmarx_projects):
    """
    Compares GitHub repositories with Checkmarx projects and returns lists of matches and non-matches.

    This function iterates through the GitHub repositories and checks if each repository's name
    exists in the Checkmarx projects. It returns two lists:
    - A list of repositories that have matching project names in Checkmarx.
    - A list of repositories that do not have matching project names in Checkmarx.

    Args:
        github_repositories (dict): A dictionary of GitHub repositories where the keys are repository names
                                    and the values are dictionaries containing repository details, including a 'name' key.
        checkmarx_projects (dict): A dictionary of Checkmarx projects where the keys are project names
                                   and the values are dictionaries containing project details, including a 'proj_name' key.

    Returns:
        tuple: A tuple containing two lists:
               - matches (list): A list of dictionaries representing GitHub repositories that have matching project names in Checkmarx.
               - non_matches (list): A list of dictionaries representing GitHub repositories that do not have matching project names in Checkmarx.
    """
    matches = []
    non_matches = []
    
    for key1, value1 in github_repositories.items():
        name1 = value1.get('name')
        found_match = False
        for key2, value2 in checkmarx_projects.items():
            proj_name2 = value2.get('proj_name')
            if name1 == proj_name2:
                matches.append(value1)
                found_match = True
                break  # Stop searching once a match is found
        if not found_match:
            non_matches.append(value1)

    return matches, non_matches

def printlist (data, filename_prefix):
    """
    Writes a list of data to a CSV file with a timestamp in the filename.

    Parameters:
    data (list of dicts): A list of dictionaries to write to the CSV file.
    filename_prefix (str): The prefix for the filename. The final filename will include this prefix and a timestamp.

    Returns:
    None
    """
    try:
        # Get the current timestamp and format it
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create the complete filename with the timestamp
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        # Extract headers from the first dictionary in the array
        headers = list(data[0].keys())

        # Open the file in write mode
        with open(filename, 'w') as file:
            # Write the header
            file.write(','.join(headers) + '\n')
            
            # Write the rows
            for row in data:
                values = [str(row.get(header, "")) for header in headers]
                file.write(','.join(values) + '\n')

        print(f"Data has been written to {filename}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except IndexError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch repositories from GitHub and projects from Checkmarx One.")
    parser.add_argument('--github-user-or-org', type=str, required=True, help="GitHub username or organization name")
    parser.add_argument('--github-api-key', type=str, required=True, help="GitHub API token to access private repos")
    parser.add_argument('--number-of-projects', type=int, required=True, help="Number of projects for GitHub & Checkmarx")
    parser.add_argument('--checkmarx-api-key', type=str, required=True, help="JWT token for Checkmarx One API")
    args = parser.parse_args()

    github_repositories = list_github_repositories(args.github_user_or_org, args.github_api_key, args.number_of_projects)
    checkmarx_projects = list_checkmarx_projects(args.checkmarx_api_key)

    total_repos = len(github_repositories)

    matches,non_matches = compare_lists (github_repositories, checkmarx_projects)

    total_matches = len(matches)

    print (f"Percentage of GitHub repos covered {total_matches / total_repos * 100}%")

    printlist (matches, 'output-found')
    printlist (non_matches, 'output-notfound')
