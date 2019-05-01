from flask import jsonify, request
from app import app
import subprocess
import json
import ast
import os

class PackageBehavior():
  def __init__(self, data=None, args=None):
    self.data = {}
    self.args = {}

    if data:
      self.data = data
    elif request.get_json():
      self.data = request.get_json(force=True)

    if args:
      self.args = args
    elif request.args:
      self.args = request.args

    self.proj_lang = app.config['PROJ_LANG']
    self.config_dir = app.config['CONFIG_DIR']
    self.package_path = '{}/installed_packages.json'.format(self.config_dir)

    # Always make sure our package_json has been created
    if not os.path.isfile(self.package_path):
      self.populate_package_json()

  def get_packages(self):
    with open(self.package_path) as json_file:
      package_json = json.load(json_file)

    if 'expand' in self.args.keys():
      return jsonify(package_json)

    res = {"userInstalled": package_json['userInstalled']}
    return jsonify(res)

  def package_install(self):
    data = self.data
    # Get the containers package_json & create one if it's not present
    with open(self.package_path) as json_file:
      package_json = json.load(json_file)

    # Loop thorugh packages in data and try to install each one
    result = {'installed': [], 'failed': []}
    for package in data.get('packages'):
      res = self.pip_install(package)
      if 'installed' in res.keys():
        result['installed'].append(package)
      else:
        result['failed'].append(package)

    # Record the installed packaged in the package_json
    if result.get('installed'):
      package_json['userInstalled'].extend(result['installed'])
      package_json['installed'].extend(result['installed'])
      ui_list = list({v['name']:v for v in package_json['userInstalled']}.values())
      installed_list = list({v['name']:v for v in package_json['installed']}.values())
      package_json['userInstalled'] = ui_list
      package_json['installed'] = installed_list

    with open(self.package_path, 'w+') as outfile:
      json.dump(package_json, outfile)

    return jsonify(package_json)

  def pip_install(self, package):
    package_name = package.get('name')
    package_version = package.get('version')
    cmd = ['pip', 'install']
    if package_version:
      name_version = '{}=={}'.format(package_name, package_version)
      cmd.append(name_version)
    else:
      cmd.append(package_name)

    try:
      res = subprocess.run(cmd, capture_output=True, encoding='UTF-8', check=True)
      return {'installed': package_name}

    except subprocess.CalledProcessError as e:
      return {'failed': {'name': package_name, 'error': e.stderr}}

  def populate_package_json(self):
    res = subprocess.run(['pip', 'list', '--format', 'json'], capture_output=True, encoding='UTF-8')
    package_list = ast.literal_eval(res.stdout)

    installed_packages = {
        "userInstalled": [],
        "installed": package_list
        }

    with open(self.package_path, 'w+') as outfile:
      json.dump(installed_packages, outfile)

    return installed_packages

  def restart_process(self):
    res = subprocess.run(['supervisorctl', 'restart', 'app'], capture_output=True, encoding='utf-8')
    return jsonify(res.stdout.split('\n'))
