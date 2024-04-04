from bitbucket_pipes_toolkit import Pipe

schema = {
  'TF_API_TOKEN': {'type': 'string', 'required': True},
  'TF_ORG_NAME': {'type': 'string', 'required': True},
  'TF_WORKSPACE_NAME': {'type': 'string', 'required': True},
  'TF_PROJECT_NAME': {'type': 'string', 'required': True},
}

def create_workspace():
    pass

class DemoPipe(Pipe):
    def run(self):
        super().run()

        ## Variables setup
        API_TOKEN = self.get_variable('TF_API_TOKEN')
        ORG_NAME = self.get_variable('TF_ORG_NAME')
        WORKSPACE_NAME = self.get_variable('TF_WORKSPACE_NAME')
        PROJECT_NAME = self.get_variable('TF_PROJECT_NAME')


        ## !!

        self.success(message="Success!")


if __name__ == '__main__':
    pipe = DemoPipe(pipe_metadata='/pipe.yml', schema=schema)
    pipe.run()