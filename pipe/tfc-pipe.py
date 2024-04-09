from bitbucket_pipes_toolkit import Pipe, get_logger
import json, requests

schema = {
  'TF_API_TOKEN': {'type': 'string', 'required': True},
  'TF_ORG_NAME': {'type': 'string', 'required': True},
  'TF_NEW_WORKSPACE_NAME': {'type': 'string', 'required': True},
  'TF_PROJECT_NAME': {'type': 'string', 'required': False},
}

## Get ID from project name
def get_project_id(API_KEY, ORG_NAME, PROJECT_NAME):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/projects?filter%5Bnames%5D={PROJECT_NAME}"

    api_headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(api_endpoint, headers=api_headers)

    if response.status_code == 200:
        data = response.json()
        project_id = data['data'][0]['id'] if 'data' in data and data['data'] else None

        return project_id
    else:
        print(f"Error: {response.status_code}")
        return None


## Workspace creation and association
def create_workspace(API_KEY, ORG_NAME, NEW_WORKSPACE_NAME, PROJECT_NAME):

    if PROJECT_NAME:
        project_id = get_project_id(API_KEY, ORG_NAME, PROJECT_NAME)

        payload = {
            "data": {
                "attributes": {
                    "name": NEW_WORKSPACE_NAME,
                    "resource-count": 0,
                    "updated-at": "03-04-2024"
                },
                "type": "workspaces",
                "relationships": {
                    "project": {
                        "data": {
                            "id": project_id,
                            "type": "projects"
                        } 
                    }   
                }
            }
        }
    else:
        payload = {
            "data": {
                "attributes": {
                    "name": NEW_WORKSPACE_NAME,
                    "resource-count": 0,
                    "updated-at": "03-04-2024"
                },
                "type": "workspaces",
            }
        }


    payload_json = json.dumps(payload)

    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces"

    api_headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.post(api_endpoint, headers=api_headers, data=payload_json)

    if response.status_code == 201:
        print("Workspace created successfully.")
    elif (response.status_code == 422):
        print("Workspace already exists, but process will continue!")
    else:
        print("Failed to create workspace. Status code:", response.status_code)


logger = get_logger()

class CreateWorkspacePipe(Pipe):
    def run(self):
        super().run()

        ## Variables setup
        API_TOKEN = self.get_variable('TF_API_TOKEN')
        ORG_NAME = self.get_variable('TF_ORG_NAME')
        NEW_WORKSPACE_NAME = self.get_variable('TF_NEW_WORKSPACE_NAME')
        PROJECT_NAME = self.get_variable('TF_PROJECT_NAME')

        create_workspace(API_TOKEN, ORG_NAME, NEW_WORKSPACE_NAME, PROJECT_NAME)


if __name__ == '__main__':
    pipe = CreateWorkspacePipe(pipe_metadata='/pipe.yml', schema=schema)
    pipe.run()