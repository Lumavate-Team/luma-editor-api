from lumavate_service_util import RestBehavior
from flask import jsonify, request, g
from pathlib import Path
import os

class EditorBehavior(RestBehavior):
  def __init__(self):
    self.project_config = {
        'widget': '/app/',
        'dep': '/other_path/'
        }

    super().__init__(None)

  def get_info(self):
    return jsonify(self.project_config)

  def validate_path(self, root, path):
    req_root = self.project_config.get(root)
    if not req_root:
      raise Exception('Path does not exsist')

    if path:
      new_path = '{}{}'.format(req_root, path)
    else:
      new_path = req_root

    if not os.path.exists(new_path):
      raise Exception('Path does not exsist')

    return new_path

  def stat(self, root, path):
    path = self.validate_path(root, path)

    res = None
    if os.path.isfile(path):
      res = {
          "path": path,
          'root': self.project_config.get(root),
          "type": 1
          }
    elif os.path.isdir(path):
      res = {
          "path": path,
          'root': self.project_config.get(root),
          "type": 2
          }
    else:
      raise Exception('Invalid path')

    return jsonify(res)

  def read(self, root, req_path):
    path = self.validate_path(root, req_path)

    res = None
    if os.path.isfile(path):
      contents = Path(path).read_text()
      res = {
          "path": req_path,
          "contents": contents,
          'root': self.project_config.get(root),
          "type": 1
          }
    elif os.path.isdir(path):
      dir_contents = os.listdir(path)
      contents = []

      for entry in dir_contents:
        full_path = '{}{}'.format(self.append_slash(path), entry)
        is_file = os.path.isfile(full_path)
        contents.append({'name': entry, 'path': self.append_slash(req_path), 'type': 1 if is_file else 2, 'contents': None})

      res = {
          "path": self.append_slash(req_path),
          "contents": contents,
          'root': self.project_config.get(root),
          "type": 2
          }
    else:
      raise Exception('Invalid path')

    return jsonify(res)

  def append_slash(self, path):
    if not path.endswith('/'):
      return path + '/'

    return path

  def create(self, root, path):
    req_root = self.project_config.get(root)
    if not req_root:
      raise Exception('Path does not exsist')

    if path:
      new_path = '{}{}'.format(req_root, path)
    else:
      new_path = req_root

    if os.path.exists(new_path):
      raise Exception('Path already exsists')

    os.mkdir(new_path)

  def delete(self, root, path):
    pass

  def write(self, root, path):
    path = self.validate_path(root, path)

    with open(path, 'w') as f:
      f.write(content)

    return jsonify('ok')
