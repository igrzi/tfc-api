# tfc-api.sh

```
  ____________________                __   ___    ____  ____
 /_  __/ ____/ ____/ /___  __  ______/ /  /   |  / __ \/  _/
  / / / /_  / /   / / __ \/ / / / __  /  / /| | / /_/ // /  
 / / / __/ / /___/ / /_/ / /_/ / /_/ /  / ___ |/ ____// /   
/_/ /_/    \____/_/\____/\____/\____/  /_/  |_/_/   /___/

```

This script provides a command-line interface for interacting with the Terraform Cloud API. It includes functions for listing workspaces, creating a workspace, listing projects, creating a project, and attaching a workspace to a project.

## Usage
The script requires two, three or four arguments depending on the function:

- **API_KEY**: The API key used for authentication with the Terraform Cloud API.
- **ORGANIZATION_NAME**: The name of the organization in Terraform Cloud.
- **PROJECT_NAME**: The name of the project in Terraform Cloud.
- **WORKSPACE_NAME**: The name of the workspace you want to attatch a projec to.

### Functions
- `show_menu`: Displays the menu of available options.  

- `list_workspaces`: Lists all workspaces for the given organization.  

- `create_workspace`: Creates a new workspace for the given organization. 

- `list_projects`: Lists all projects for the given organization.  

- `create_project`: Creates a new project for the given organization.  

- `attach_workspace_to_project`: Attaches a workspace to a project.
  
### Dependencies
This script requires `curl` and `jq` to be installed on your system.

### Contributing
Pull requests are welcome!

### License  
MIT
