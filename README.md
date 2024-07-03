# compare_gh_and_cx

GitHub and Checkmarx Projects Comparison Tool
This Python tool fetches repositories from a specified GitHub user or organization and projects from Checkmarx. It then compares the two lists to find matches and non-matches, outputting the results to CSV files.

## Features
- Fetches repositories from GitHub using the GitHub API.
- Fetches projects from Checkmarx using the Checkmarx API.
- Compares GitHub repositories with Checkmarx projects.
- Outputs the comparison results to CSV files.

## Requirements

- Python 3.x
- `requests` module

You can install the requests module using pip:

```sh
pip install requests
```
## Usage
To use the tool, run the script with the following command-line arguments:

* --github-user-or-org: GitHub username or organization name
* --github-api-key: GitHub API token to access private repos
* --number-of-projects: Number of projects for GitHub and Checkmarx
* --checkmarx-api-key: JWT token for Checkmarx API

## Example
```sh
python script.py --github-user-or-org my-org --github-api-key my-github-token --number-of-projects 1000 --checkmarx-api-key my-checkmarx-token
```

# GitHub and Checkmarx Project Comparison Tool

This Python script retrieves repositories from a specified GitHub user or organization and projects from Checkmarx One, then compares them to identify matches and non-matches. The results are saved to CSV files.

## Features
- Fetches repositories from GitHub.
- Authenticates with Checkmarx One to retrieve projects.
- Compares GitHub repositories with Checkmarx projects to identify matches and non-matches.
- Saves the results to CSV files with timestamps.

## Requirements
- Python 3.x
- requests library

You can install the requests module using pip:

```sh
pip install requests
```

## Usage
Run the script from the command line with the necessary arguments:

* --github-user-or-org: GitHub username or organization name.
* --github-api-key: GitHub API token to access private repositories.
* --number-of-projects: Number of projects to retrieve from both GitHub and Checkmarx.
* --checkmarx-api-key: JWT token for Checkmarx One API.

## Example
```sh
python script.py --github-user-or-org example_user --github-api-key your_github_token --number-of-projects 50 --checkmarx-api-key your_checkmarx_api_key
```
