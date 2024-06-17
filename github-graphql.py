import requests
import os
import json

api_token = os.environ["GITHUB_API_TOKEN"]
gitlab_api_token = os.environ["GITLAB_PA_TOKEN"]

url = os.environ["GRAPHQL_ENDPOINT"]

get_repositories_query_temp = {
        'query': '''{
		viewer {
			repositories(first: 30) {
				totalCount pageInfo {
					hasNextPage endCursor
				}
				edges {
					node {
						name
					}
				}
			}
		}
	}'''
}
get_repositories_query = '''{
		viewer {
			name
			repositories(last: 30) {
				nodes {
				name
			url
				}
			}
		}
	}'''

get_org_query = '''{
			organization(login:"MH-Migration-Org") {
				name
				id
			}
		}'''

get_issues_query = '''{
		repository(owner:"mandar-harkare", name:"nodejs") {
			issues(last:20) {
				edges {
					node {
						title
						url
						labels(first:5) {
							edges {
								node {
									name
								}
							}
						}
					}
				}
			}
		}
	}'''


def run_graphql_query(query):
    headers = {'Authorization': 'token %s' % api_token}
    data = {'query': query}
    return json.loads(requests.post(url=url, json=data, headers=headers).text)


# r = requests.post(url=url, json=getIssuesQuery, headers=headers)
def get_organization():
    response = run_graphql_query(get_org_query)
    print(response["data"]["organization"])
    return response["data"]["organization"]


def create_repository_migration(repo_name, repo_url, organization_id):
    graphql_mutation = """
		mutation {
			createMigrationSource(
				input: {
					name: "%s",
					url: "%s",
					ownerId: "%s",
					type: AZURE_DEVOPS
				}
			) {
				migrationSource {
					id
				}
			}
		}
	""" % (repo_name, repo_url, organization_id)
    response = run_graphql_query(graphql_mutation)
    print(response)
    return response["data"]


def start_repository_migration(repo_name, repo_url, organization_id):

    start_repository_migration_mutation = """
		mutation {
			startRepositoryMigration(
				input: {
					sourceId: "%s",
					repositoryName: "%s",
					ownerId: "%s",
					sourceRepositoryUrl: "%s",
					continueOnError: true,
					targetRepoVisibility: "%s",
					githubPat: "%s",
					accessToken: "%s"
				}
			) {
				repositoryMigration {
					id
				}
			}
		}
	""" % (
        migration_id,
        repo_name,
        organization_id,
        repo_url,
        "private",
        api_token,
        gitlab_api_token
    )

    response = run_graphql_query(start_repository_migration_mutation)
    print(response)
    return response["data"]


def get_repository_migration_statu(start_migration_id):
	get_repository_migration_status = """{
		node (id:"%s"){
			... on Migration {

				migrationSource {
					name
					id
				}
				state
				failureReason
			}
		}
	}"""% (
        start_migration_id
    )

	response = run_graphql_query(get_repository_migration_status)
	print(response)
	return response["data"]


organization_id = get_organization()["id"]
#"MS_kgDaACQ0Mzg1NzA0Mi00MTdkLTRmODQtYTJlYi1jYzU0NTE3MDdmMjE"
migration_id = create_repository_migration(
    "research-hub",
    "https://gitlab.com/mandar.harkare/research-hub",
    organization_id
)["createMigrationSource"]["migrationSource"]["id"]

start_migration_id = start_repository_migration(
    "research-hub",
    "https://gitlab.com/mandar.harkare/research-hub",
    organization_id
)["startRepositoryMigration"]["repositoryMigration"]["id"]

get_repository_migration_statu(start_migration_id)
