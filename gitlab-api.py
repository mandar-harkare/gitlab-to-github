import gitlab
import requests
import os
# private token or personal token authentication
gl = gitlab.Gitlab(os.environ['GITLAB_URL'], private_token=os.environ['GITLAB_PA_TOKEN'], api_version=4)
gl.auth()

projects = gl.projects.list(owned=True, search='hub')
# items = projects.repository_tree()
for project in projects:
	print(project.name)
	print(project.ssh_url_to_repo)
	branches = project.branches.list()
	for branch in branches:
		print("-->"+branch.name)