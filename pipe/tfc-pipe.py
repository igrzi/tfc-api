from bitbucket_pipes_toolkit import Pipe, get_logger
import json, requests

schema = {
  'TF_API_TOKEN': {'type': 'string', 'required': True},
  'TF_ORG_NAME': {'type': 'string', 'required': True},
  'TF_NEW_WORKSPACE_NAME': {'type': 'string', 'required': True},
  'TF_PROJECT_NAME': {'type': 'string', 'required': False},
  'TF_REMOTE_STATE_SHARE': {'type': 'string', 'required': False}
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
def create_workspace(API_KEY, ORG_NAME, NEW_WORKSPACE_NAME, PROJECT_NAME, REMOTE_STATE_SHARE, pipe):

    payload = {
    "data": {
        "attributes": {
            "name": NEW_WORKSPACE_NAME,
            "resource-count": 0,
            "updated-at": "03-04-2024",
            "global-remote-state": REMOTE_STATE_SHARE or False      ## If TF_REMOTE_STATE_SHARE is not provided, default to False
        },
        "type": "workspaces",
        **({"relationships": {"project": {"data": {"id": get_project_id(API_KEY, ORG_NAME, PROJECT_NAME), "type": "projects"}}}} if PROJECT_NAME else {})
        ## If TF_PROJECT_NAME is provided, get the project ID and associate it with the workspace
        }
    }


    payload_json = json.dumps(payload)

    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces"

    api_headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {API_KEY}"
    }


    response = requests.post(api_endpoint, headers=api_headers, data=payload_json)


    if response.status_code == 401:
        pipe.fail("Unauthorized. Check your API token.", response.status_code)
    elif response.status_code == 201:
        pipe.success("Workspace created successfully.")
    elif response.status_code == 422 and response.json()['errors'][0]['detail'] == "Name has already been taken":
        pipe.success("Workspace already exists, but process will continue!")
    else:
        pipe.fail(f"Failed to create workspace. {response.json()['errors'][0]['detail']}")


logger = get_logger()

class CreateWorkspacePipe(Pipe):
    def run(self):
        super().run()

        ## Variables setup
        API_TOKEN = self.get_variable('TF_API_TOKEN')
        ORG_NAME = self.get_variable('TF_ORG_NAME')
        NEW_WORKSPACE_NAME = self.get_variable('TF_NEW_WORKSPACE_NAME')
        PROJECT_NAME = self.get_variable('TF_PROJECT_NAME')
        REMOTE_STATE_SHARE = self.get_variable('TF_REMOTE_STATE_SHARE')



        if workspace 
            create_workspace(API_TOKEN, ORG_NAME, NEW_WORKSPACE_NAME, PROJECT_NAME, REMOTE_STATE_SHARE, self)
        else:
            atualizar_workspace


if __name__ == '__main__':
    pipe = CreateWorkspacePipe(schema=schema)
    pipe.run()