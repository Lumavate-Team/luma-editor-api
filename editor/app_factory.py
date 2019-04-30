from flask import Flask
import subprocess
import json
import os

def create_app():
    app = Flask(__name__)

    def init_config(config_path=None):
      root = os.environ.get('PROJECT_ROOT')
      lang = os.environ.get('LANGUAGE')

      if lang:
        if lang not in ['python', 'go']:
          raise Exception("The editor currently supports 'python' and 'go'")
      else:
        try:
          res = subprocess.run(['go'], check=True)
          # Go is installed so it's probably a go widget
          lang = 'go'
        except:
          # Default to python
          lang = 'python'

      if root:
        if not os.path.isfile(root):
          raise Exception("Invalid path provided for the project root")
      else:
        # Let's find the root by looking for our standard project struct
        if os.path.isdir('/app'):
          root = '/app'
        elif os.path.isdir('/go/src/widget'):
          root = '/go/src/widget'
        else:
          raise Exception("Could not locate project root. Set the path for the root with the 'PROJECT_ROOT' ENV variable")

      # Look for luma_config dir inside project root
      config_dir = '{}/.luma_config'.format(root)
      if not os.path.isdir(config_dir):
        os.mkdir(config_dir)

      # Grab config info from config.json
      # Create the config.json if it's not there or it's empty
      config_path = '{}/config.json'.format(config_dir)
      if not os.path.isfile(config_path) or os.stat(config_path).st_size == 0:
        config_data = {
            "projectStructure": {"app": root},
            "language": lang
            }

        with open(config_path, 'w+') as outfile:
          json.dump(config_data, outfile)

      with open(config_path) as json_file:
        config_json = json.load(json_file)

      proj_struct = config_json.get('projectStructure')
      if not proj_struct:
        # If the config file doesn't define the proj struct then use the default
        proj_struct = {"app": root}

      proj_lang = config_json.get('language')
      if not proj_lang:
        # If the config file doesn't define the proj lang then make sure to add it
        proj_lang = lang

      app.config['PROJ_STRUCT'] = proj_struct
      app.config['CONFIG_DIR'] = config_dir
      app.config['PROJ_LANG'] = proj_lang

    init_config()
    return app
