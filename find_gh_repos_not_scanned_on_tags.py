import requests
import json
import argparse
import sys
import datetime

def list_github_repositories(user_or_org, token, num_of_projects):
    """
    Retrieves a specified number of repositories for a given GitHub user or organization.

    Parameters:
    user_or_org (str): The GitHub username or organization name.
    num_of_projects (int): The number of repositories to retrieve.
    token (str, optional): The GitHub API token for authentication. Defaults to None.

    Returns:
    list: A list of repository names.
    """
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
    
    repo = [item["name"] for item in repos]

    return repo

def list_checkmarx_projects(api_key):
    """
    Authenticates with the Checkmarx IAM service using a refresh token and retrieves
    the GitHub tagged repositories from Checkmarx AST.

    Parameters:
    api_key (str): The refresh token used for authentication.

    Returns:
    list: A list of GitHub tagged repositories retrieved from Checkmarx AST.
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

    url = "https://deu.ast.checkmarx.net/api/projects/tags"
    headers = {
        'Accept': 'application/json; version=1.0',
        'Authorization': f'Bearer {jwt_token}'
    }

    github_tagged_respoitories = requests.get(url, headers=headers).json()['GITHUB_REPOSITORY']

    return github_tagged_respoitories


def compare_lists(github_repositories, checkmarx_projects):
    """
    Separates items from github_repositories into matches and non_matches
    based on their presence in checkmarx_projects.

    Parameters:
    github_repositories (list): A list of GitHub repository names or IDs.
    checkmarx_projects (list): A list of Checkmarx project names or IDs.

    Returns:
    tuple: Two lists - the first containing items that are present in both 
    github_repositories and checkmarx_projects (matches), and the second 
    containing items that are only in github_repositories (non_matches).
    """
    matches = []
    non_matches = []

    for item in github_repositories:
        if item in checkmarx_projects:
            matches.append(item)
        else:
            non_matches.append(item)
    
    return matches, non_matches

def printlist (data, filename_prefix):
    """
    Writes a list of data to a CSV file with a timestamp in the filename.

    Parameters:
    data (list): A list of data to write to the CSV file. Each item in the list can be a list or any other type.
    filename_prefix (str): The prefix for the filename. The final filename will include this prefix and a timestamp.

    Returns:
    None
    """
    try:
        # Get the current timestamp and format it
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create the complete filename with the timestamp
        filename = f"{filename_prefix}_{timestamp}.csv"

        # Open the file in write mode
        with open(filename, 'w') as file:
            # Iterate over each item in the data list
            for item in data:
                # If the item is a list, join its elements with commas
                if isinstance(item, list):
                    file.write(','.join(map(str, item)) + '\n')
                else:
                    # If the item is not a list, write it directly
                    file.write(str(item) + '\n')
        print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"An IOError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch repositories from GitHub and projects from Checkmarx One.")
    parser.add_argument('--github-user-or-org', type=str, required=True, help="GitHub username or organization name")
    parser.add_argument('--github-api-key', type=str, required=True, help="GitHub API token to access private repos")
    parser.add_argument('--number-of-projects', type=int, required=True, help="Number of projects for GitHub & Checkmarx")
    parser.add_argument('--checkmarx-api-key', type=str, required=True, help="JWT token for Checkmarx One API")
    args = parser.parse_args()

    github_repositories = list_github_repositories(args.github_user_or_org, args.github_api_key, args.number_of_projects)
    checkmarx_tags = list_checkmarx_projects(args.checkmarx_api_key)

    total_repos = len(github_repositories)

    matches,non_matches = compare_lists (github_repositories, checkmarx_tags)

    percentage_matches = (len(matches) / total_repos) * 100

    print(f"Percentage of total matches: {percentage_matches:.2f}%")

    printlist (matches, 'output-found')
    printlist (non_matches, 'output-notfound')
