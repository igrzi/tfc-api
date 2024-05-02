# TFC-Pipe


## Quick access

### [Pipeline Example](#bitbucket-pipelinesyml-example)
### [Variables](#variables)
### [Author Information](#author-information)


## *bitbucket-pipelines.yml* example

    pipelines:
    default:
        - step:
            name: pipeline-test-0.1.8
            script:
            - pipe: docker://igrzi1/create_tfc_workspace:0.1.8
                variables:
                TF_API_TOKEN: $TF_API_TOKEN
                TF_ORG_NAME: $TF_ORG_NAME
                TF_WORKSPACE_NAME: $TF_WORKSPACE_NAME
                TF_PROJECT_NAME: $TF_PROJECT_NAME
                TF_REMOTE_STATE_SHARE: $TF_REMOTE_STATE_SHARE


## Variables

### TF_API_TOKEN
This is your ***Terraform Cloud API Token***, it can be the *Organization* API Token or the *User* API Token.

### TF_ORG_NAME
This is the name of your ***Terraform Cloud Organization***, be careful as this is case sensitive.

### TF_WORKSPACE_NAME
This is the name of the ***Terraform Cloud Workspace*** you either want to: Create, associate a project to or change the remote state.

### TF_PROJECT_NAME
This is the name of the ***Terraform Cloud Project*** you want to associate to a already created workspace or a newly created one.

### TF_REMOTE_STATE_SHARE
This is **boolean** value that determines whether this workspace should share state with the entire organization, or only with specific approved workspaces.


## Author Information

### [GitHub](https://github.com/igrzi) profile
### [LinkedIn](https://www.linkedin.com/in/igrzi) profile