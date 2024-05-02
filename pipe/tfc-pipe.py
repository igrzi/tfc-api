from bitbucket_pipes_toolkit import Pipe, get_logger
import json, requests

schema = {
  'TF_API_TOKEN': {'type': 'string', 'required': True},
  'TF_ORG_NAME': {'type': 'string', 'required': True},
  'TF_WORKSPACE_NAME': {'type': 'string', 'required': True},
  'TF_PROJECT_NAME': {'type': 'string', 'required': False},
  'TF_REMOTE_STATE_SHARE': {'type': 'string', 'required': False}
}

"""
create_headers() | Tool Function

This function receives the API_TOKEN as parameter and returns the headers to be used in the requests.

Input: API_TOKEN
"""
def create_headers(API_TOKEN):
    return {
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {API_TOKEN}"
    }


"""
check_if_workspace_exists() | Tool Function | GET

This function receives the API_TOKEN, ORG_NAME and WORKSPACE_NAME as parameters and returns True if the workspace exists (200 status code), otherwise, it returns False.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME
Output: True or False

"""
def check_if_workspace_exists(API_TOKEN, ORG_NAME, WORKSPACE_NAME):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces/{WORKSPACE_NAME}"
    
    response = requests.get(api_endpoint, headers=create_headers(API_TOKEN))

    if response.status_code == 200:
        return True
    else:
        return False
    

"""
get_workspace_id() | Tool Function | GET

This function receives the API_TOKEN, ORG_NAME and WORKSPACE_NAME as parameters and returns the workspace_id if it exists (200 status code), otherwise, it returns breaks.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME
Output: workspace_id or None

"""
def get_workspace_id(API_TOKEN, ORG_NAME, WORKSPACE_NAME):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces?filter%5Bnames%5D={WORKSPACE_NAME}"
    
    response = requests.get(api_endpoint, headers=create_headers(API_TOKEN))

    if response.status_code == 200:
        data = response.json()
        workspace_id = data['data'][0]['id'] if 'data' in data and data['data'] else None
        return workspace_id
    else:
        pipe.fail(f"Workspace not found, check workspace name", response.status_code)


"""
get_project_id() | Tool Function | GET

This function receives the API_TOKEN, ORG_NAME and PROJECT_NAME as parameters and returns the project_id if it exists (200 status code), otherwise, it breaks the pipeline.

Input: API_TOKEN, ORG_NAME, PROJECT_NAME
Output: project_id or Pipeline break

"""
def get_project_id(API_TOKEN, ORG_NAME, PROJECT_NAME):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/projects?filter%5Bnames%5D={PROJECT_NAME}"

    response = requests.get(api_endpoint, headers=create_headers(API_TOKEN))

    if response.status_code == 200:
        data = response.json()
        project_id = data['data'][0]['id']

        return project_id
    else:
        pipe.fail(f"Project ID not found, check project name", response.status_code)

"""
current_remote_state() | Tool Function | GET

This function receives the API_TOKEN, ORG_NAME and WORKSPACE_NAME as parameters and returns the current remote state of the workspace.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME
Output: remote_state or Pipe fail
"""
def current_remote_state(API_TOKEN, ORG_NAME, WORKSPACE_NAME):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces?filter%5Bnames%5D={WORKSPACE_NAME}"

    response = requests.get(api_endpoint, headers=create_headers(API_TOKEN))

    if response.status_code == 200:
        data = response.json()
        remote_state = data['data'][0]['attributes']['global-remote-state']

        # False = Share with specific workspaces
        # True  = Share with all workspaces
        return str(remote_state).lower()
    else:
        pipe.fail(f"Workspace not found, check workspace name", response.status_code)


"""
current_workspace_project_id() | Tool Function | GET

This function receives the API_TOKEN, ORG_NAME and WORKSPACE_NAME as parameters and returns the current project id of the workspace.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME
Output: project_id or None
"""
def current_workspace_project_id(API_TOKEN, ORG_NAME, WORKSPACE_NAME, pipe):
    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces?filter%5Bnames%5D={WORKSPACE_NAME}"

    response = requests.get(api_endpoint, headers=create_headers(API_TOKEN))

    if response.status_code == 200:
        data = response.json()
        project_id = data['data'][0]['relationships']['project']['data']['id']

        return project_id
    else:
        pipe.fail("Workspace not found, check workspace name", response.status_code)

"""
associate_workspace_to_project() | Core Function | PATCH

This function receives the API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME as parameters and associates the project to a already created workspace.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME
Output: Pipeline success or fail 

"""
def associate_workspace_to_project(API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME, pipe):
    
    payload = {
    "data": {
        "attributes": {
            "name": WORKSPACE_NAME,
            "resource-count": 0,
            "updated-at": "03-04-2024"
        },
        "type": "workspaces",
        **({"relationships": {"project": {"data": {"id": get_project_id(API_TOKEN, ORG_NAME, PROJECT_NAME), "type": "projects"}}}} if PROJECT_NAME else {})
        }
    }


    payload_json = json.dumps(payload)

    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces/{WORKSPACE_NAME}"

    response = requests.patch(api_endpoint, headers=create_headers(API_TOKEN), data=payload_json)

    if response.status_code == 401:
        pipe.fail("Unauthorized. Check your API token.", response.status_code)
    elif response.status_code == 200:
        pipe.success("Project associated successfully.")
    else:
        pipe.fail(f"Not covered error! If you want, create an issue in the repository link.", response.status_code)


"""
create_workspace() | Core Function | POST

This function receives the API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME* and REMOTE_STATE_SHARE* as parameters and creates a new workspace.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME*, REMOTE_STATE_SHARE*
Output: Pipeline success or fail

Variables with * are optional.

If PROJECT_NAME isn't provided, the workspace will be created with the default project. And REMOTE_STATE_SHARE will default to False if not provided.

"""
def create_workspace(API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME, REMOTE_STATE_SHARE, pipe):

    payload = {
    "data": {
        "attributes": {
            "name": WORKSPACE_NAME,
            "resource-count": 0,
            "updated-at": "03-04-2024",
            "global-remote-state": REMOTE_STATE_SHARE or False
        },
        "type": "workspaces",
        **({"relationships": {"project": {"data": {"id": get_project_id(API_TOKEN, ORG_NAME, PROJECT_NAME), "type": "projects"}}}} if PROJECT_NAME else {})
        }
    }


    payload_json = json.dumps(payload)

    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces"

    response = requests.post(api_endpoint, headers=create_headers(API_TOKEN), data=payload_json)


    if response.status_code == 401:
        pipe.fail("Unauthorized. Check your API token.", response.status_code)
    elif response.status_code == 201:
        pipe.success("Workspace created successfully.")
    elif response.status_code == 422 and response.json()['errors'][0]['detail'] == "Name has already been taken":
        pipe.success("Workspace already exists, but process will continue!")
    else:
        pipe.fail(f"Failed to create workspace. {response.json()['errors'][0]['detail']}")


"""
change_remote_state() | Core Function | PATCH

This function receives the API_TOKEN, ORG_NAME, WORKSPACE_NAME and REMOTE_STATE_SHARE* as parameters and changes the remote state of the workspace.

Input: API_TOKEN, ORG_NAME, WORKSPACE_NAME, REMOTE_STATE_SHARE*
Output: Pipeline success or fail
Variables with * are optional.

If REMOTE_STATE_SHARE isn't provided, it will default to False.

"""
def change_remote_state(API_TOKEN, ORG_NAME, WORKSPACE_NAME, REMOTE_STATE_SHARE, pipe):

    payload = {
    "data": {
        "attributes": {
            "name": WORKSPACE_NAME,
            "resource-count": 0,
            "updated-at": "03-04-2024",
            "global-remote-state": REMOTE_STATE_SHARE or False
        },
        "type": "workspaces"
        }
    }
    
    payload_json = json.dumps(payload)

    api_endpoint = f"https://app.terraform.io/api/v2/organizations/{ORG_NAME}/workspaces/{WORKSPACE_NAME}"

    response = requests.patch(api_endpoint, headers=create_headers(API_TOKEN), data=payload_json)

    if response.status_code == 401:
        pipe.fail("Unauthorized. Check your API token.", response.status_code)
    elif response.status_code == 200:
        pipe.success("Remote state updated successfully.")
    else:
        pipe.fail(f"Not covered error! If you want, create an issue in the repository link. {response.json()['errors'][0]['detail']}")


logger = get_logger()

class CreateWorkspacePipe(Pipe):
    def run(self):
        super().run()

        API_TOKEN = self.get_variable('TF_API_TOKEN')
        ORG_NAME = self.get_variable('TF_ORG_NAME')
        WORKSPACE_NAME = self.get_variable('TF_WORKSPACE_NAME')
        PROJECT_NAME = self.get_variable('TF_PROJECT_NAME')
        REMOTE_STATE_SHARE = self.get_variable('TF_REMOTE_STATE_SHARE') ## Change this to accept either it even if it's like TRUE True true

        WORKSPACE_EXISTS = check_if_workspace_exists(API_TOKEN, ORG_NAME, WORKSPACE_NAME)


        """
        If the workspace exists, it will do one or more of the following things:
            If the project id from the workspace is different from the project provided, it will associate the project to the workspace.

            If the remote state share is different from the provided, it will change the remote state of the workspace.

            If both the provided names are the same as the current ones, it will return a success message.
        
        If the workspace doesn't exist, it will:
            Try to create a new workspace with the provided project and remote state share.

            Else it will give a success message.
        """

        if WORKSPACE_EXISTS:
            if get_project_id(API_TOKEN, ORG_NAME, PROJECT_NAME) != current_workspace_project_id(API_TOKEN, ORG_NAME, WORKSPACE_NAME, self):
                associate_workspace_to_project(API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME, self)
            
            if REMOTE_STATE_SHARE != current_remote_state(API_TOKEN, ORG_NAME, WORKSPACE_NAME):
                change_remote_state(API_TOKEN, ORG_NAME, WORKSPACE_NAME, REMOTE_STATE_SHARE, self)
            
            else:
                self.success("Nothing changed.")

        elif not WORKSPACE_EXISTS:
            create_workspace(API_TOKEN, ORG_NAME, WORKSPACE_NAME, PROJECT_NAME, REMOTE_STATE_SHARE, self)

        else:
            self.success("Nothing changed.")


if __name__ == '__main__':
    pipe = CreateWorkspacePipe(schema=schema)
    pipe.run()