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

--github-user-or-org: GitHub username or organization name
--github-api-key: GitHub API token to access private repos
--number-of-projects: Number of projects for GitHub and Checkmarx
--checkmarx-api-key: JWT token for Checkmarx API

## Example
```sh
python script.py --github-user-or-org my-org --github-api-key my-github-token --number-of-projects 1000 --checkmarx-api-key my-checkmarx-token
```
