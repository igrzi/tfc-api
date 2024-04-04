#!/bin/bash

# Define a function for displaying the menu
show_menu() {
  echo -e "\e[32m
  ____________________                __   ___    ____  ____
 /_  __/ ____/ ____/ /___  __  ______/ /  /   |  / __ \/  _/
  / / / /_  / /   / / __ \/ / / / __  /  / /| | / /_/ // /  
 / / / __/ / /___/ / /_/ / /_/ / /_/ /  / ___ |/ ____// /   
/_/ /_/    \____/_/\____/\____/\____/  /_/  |_/_/   /___/

\e[0m"
  
  echo -e "\e[32mSelect an option from the menu:\e[0m"
  echo "1. List workspaces"
  echo "2. Create a workspace"
  echo "3. List projects"
  echo "4. Create a project"
  echo "5. Attach a workspace to a project"
  echo "6. Exit"
  echo ""
}

# List workspaces function
list_workspaces() {
  if [ $# -ne 2 ]; then
    echo "Usage: $0 <API_KEY> <ORGANIZATION_NAME>"
    show_menu
  else

    API_KEY=$1
    ORGANIZATION_NAME=$2

    ENDPOINT="https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/workspaces"

    # Check if request was successful
    if [ $? -ne 0 ]; then
      echo -e "\e[31mError\e[0m: Failed to make request to Terraform Workspaces API"
      exit 1
    fi

    response=$(curl -s -X GET \
                      -H "Content-Type: application/vnd.api+json" \
                      -H "Authorization: Bearer $API_KEY" \
                      "$ENDPOINT")
                      
    # Check if API response contains workspaces
    if [ -z "$(echo "$response" | jq -r '.data[].attributes.name')" ]; then
      echo ""
      echo -e "\e[33mAlert!\e[0m: No workspaces found for organization: $ORGANIZATION_NAME"
      exit 1
    else
      echo ""
      echo "Workspaces for organization: $ORGANIZATION_NAME"
      echo "$response" | jq '.data[].attributes.name'
      exit 1
    fi
  fi
}

create_workspace() {
  if [ $# -ne 3 ]; then
    echo "Usage: $0 <API_KEY> <ORGANIZATION_NAME> <WORKSPACE_NAME>"
    show_menu
  else

    API_KEY=$1
    ORGANIZATION_NAME=$2
    WORKSPACE_NAME=$3

    # Define the endpoint
    ENDPOINT="https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/workspaces"

    # Define the request payload without VCS repository
    REQUEST_PAYLOAD='
    {
      "data": {
        "attributes": {
          "name": "'"$WORKSPACE_NAME"'",
          "resource-count": 0,
          "updated-at": "03-04-2024"
        },
        "type": "workspaces"
      }
    }'

    # Make the POST request
    response=$(curl -s -X POST \
                      -H "Content-Type: application/vnd.api+json" \
                      -H "Authorization: Bearer $API_KEY" \
                      -d "$REQUEST_PAYLOAD" \
                      "$ENDPOINT")

    # Check if request was successful
    if [ $? -ne 0 ]; then
      echo "Error: Failed to make request to Terraform Workspaces API"
      exit 1
    fi

    # Check if API response contains workspaces
    if echo "$response" | grep -q '"errors":'; then
      echo "Error creating workspace:"
      echo "$response" | jq '.errors[0].detail'
      exit 1
    else
      echo ""
      echo -e "Workspace created \e[32msuccessfully\e[0m:"
      echo "$response" | jq '.data.attributes.name'
      exit 0
    fi
  fi
}

list_projects() {
  if [ $# -ne 2 ]; then
    echo "Usage: $0 <API_KEY> <ORGANIZATION_NAME>"
    show_menu
  else

    API_KEY=$1
    ORGANIZATION_NAME=$2

    # Make request to Terraform Workspaces API
    response=$(curl -s -H "Authorization: Bearer $API_KEY" "https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/projects")

    # Check if request was successful
    if [ $? -ne 0 ]; then
      echo -e "\e[31mError\e[0m: Failed to make request to Terraform Workspaces API"
      exit 1
    fi

    # Check if API response contains workspaces
    if echo "$response" | grep -q '"data":\[\]'; then
      echo ""
      echo -e "\e[33mAlert!\e[0m: No projects found for organization: $ORGANIZATION_NAME"
      exit 1
    else
      echo ""
      echo "Projects for organization: $ORGANIZATION_NAME"
      echo "$response" | jq '.data[].attributes.name'
      exit 1
    fi
  fi
}

create_project() {
  if [ $# -ne 3 ]; then
    echo "Usage: $0 <API_KEY> <ORGANIZATION_NAME> <PROJECT_NAME>"
    show_menu
  else

    API_KEY=$1
    ORGANIZATION_NAME=$2
    PROJECT_NAME=$3

    # Define the endpoint
    ENDPOINT="https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/projects"

    REQUEST_PAYLOAD='
    {
      "data": {
        "attributes": {
          "name": "'"$PROJECT_NAME"'"
        },
        "type": "projects"
      }
    }'

    # Make the POST request
    response=$(curl -s -X POST \
                      -H "Content-Type: application/vnd.api+json" \
                      -H "Authorization: Bearer $API_KEY" \
                      -d "$REQUEST_PAYLOAD" \
                      "$ENDPOINT")

    # Check if request was successful
    if [ $? -ne 0 ]; then
      echo "\e[31mError\e[0m: Failed to make request to Terraform Projects API"
      exit 1
    fi

    # Check if API response contains projects
    if echo "$response" | grep -q '"errors":'; then
      echo ""
      echo -e "\e[31mError\e[0m creating project!"
      exit 1
    else
      echo ""
      echo -e "Project created \e[32msuccessfully\e[0m:"
      echo "$response" | jq '.data.attributes.name'
      exit 0
    fi
  fi
}

# Function: get_project_id
#
# Description: This function retrieves the project ID from the Terraform Cloud API based on the provided API key, organization name, and project name.
#
# Parameters:
#   - API_KEY: The API key used for authentication with the Terraform Cloud API.
#   - ORGANIZATION_NAME: The name of the organization in Terraform Cloud.
#   - PROJECT_NAME: The name of the project in Terraform Cloud.
#
# Returns:
#   - The project ID as a string.
#
# Example usage:
#   project_id=$(get_project_id "API_KEY" "my_organization" "my_project")
#

get_project_id() {
  API_KEY=$1
  ORGANIZATION_NAME=$2
  PROJECT_NAME=$3

  ENDPOINT="https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/projects?filter%5Bnames%5D=$PROJECT_NAME"
  
  response=$(curl -s -X GET \
                    -H "Content-Type: application/vnd.api+json" \
                    -H "Authorization: Bearer $API_KEY" \
                    "$ENDPOINT")

  project_id=$(echo "$response" | jq -r '.data[0].id')
  echo "$project_id"
}



# Function: attach_workspace_to_project
#
# Description: Attaches a workspace to a project in Terraform Cloud.
#
# Parameters:
#   - API_KEY: The API key for authentication.
#   - ORGANIZATION_NAME: The name of the organization.
#   - WORKSPACE_NAME: The name of the workspace to attach.
#   - PROJECT_NAME: The name of the project to attach the workspace to.
#

attach_workspace_to_project() {
  if [ $# -ne 4 ]; then
    echo "Usage: $0 <API_KEY> <ORGANIZATION_NAME> <WORKSPACE_NAME> <PROJECT_NAME>"
    show_menu
  else

    API_KEY=$1
    ORGANIZATION_NAME=$2
    WORKSPACE_NAME=$3
    PROJECT_NAME=$4

    # Define the endpoint
    ENDPOINT="https://app.terraform.io/api/v2/organizations/$ORGANIZATION_NAME/workspaces/$WORKSPACE_NAME"

    PROJECT_ID=$(get_project_id "$API_KEY" "$ORGANIZATION_NAME" "$PROJECT_NAME")

    REQUEST_PAYLOAD='
    {
      "data": {
        "attributes": {
          "name": "'"$WORKSPACE_NAME"'",
          "resource-count": 0,
          "updated-at": "03-04-2024"
        },
        "type": "workspaces",
        "relationships": {
          "project": {
            "data": {
              "id": "'"$PROJECT_ID"'",
              "type": "projects"
            }
          }
        }
      }
    }'

    # Make the POST request
    response=$(curl -s -X PATCH \
                      -H "Content-Type: application/vnd.api+json" \
                      -H "Authorization: Bearer $API_KEY" \
                      -d "$REQUEST_PAYLOAD" \
                      "$ENDPOINT")

    # Check if request was successful
    if [ $? -ne 0 ]; then
      echo "Error: Failed to make request to Terraform Workspaces API"
      exit 1
    fi

    # Check if API response contains workspaces
    if echo "$response" | grep -q '"errors":'; then
      echo "Error attatching workspace:"
      echo "$response" | jq '.errors[0].detail'
      exit 1
    else
      echo ""
      echo -e "Workspace attatched \e[32msuccessfully\e[0m!"
      echo "$response" | jq '.data.attributes.id'
      exit 0
    fi
  fi
}

# ======================================================================== #

options_screen() {
    case $1 in
        1) # List Workspaces
          list_workspaces "$2" "$3"
          ;; 
        2) # Create Workspace
          read -p "Enter workspace name: " name
          create_workspace "$2" "$3" "$name"
          ;;
        3) # List Projects
          list_projects "$2" "$3"
          ;;
        4) # Create Project
          read -p "Enter project name: " name
          create_project "$2" "$3" "$name"
          ;;
        5) # Attach a workspace to a project
          read -p "Enter workspace name: " workspace_name
          read -p "Enter project name: " project_name
          attach_workspace_to_project "$2" "$3" "$workspace_name" "$project_name"
          ;;
        6)
          echo "Exiting..."
          exit 0
          ;;
        *)
          echo "Invalid option"
          ;;
    esac
}

# Main script
while true; do
    show_menu
    read -p "Enter your choice: " choice
    case $choice in
        1|2|3|4|5)
          read -p "Enter API key: " api_key
          read -p "Enter organization name: " org_name
          options_screen $choice "$api_key" "$org_name"
          ;;
        6)
          options_screen $choice
          ;;
        *)
          echo "Invalid option"
          ;;
    esac
done
