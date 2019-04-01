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
      raise Exception('Invalid path')

    if path:
      return '{}{}'.format(req_root, path)
    else:
      return req_root

  def stat(self, root, path):
    path = self.validate_path(root, path)

    res = None
    if os.path.isfile(path):
      res = {
          "path": path,
          "type": 1
          }
    elif os.path.isdir(path):
      res = {
          "path": path,
          "type": 2
          }
    else:
      raise Exception('Invalid path')

    return jsonify(res)

  def read(self, root, path):
    path = self.validate_path(root, path)

    res = None
    if os.path.isfile(path):
      contents = Path(path).read_text()
      res = {
          "path": path,
          "contents": contents,
          "type": 1
          }
    elif os.path.isdir(path):
      dir_contents = os.listdir(path)
      contents = []

      for entry in dir_contents:
        full_path = '{}{}'.format(self.append_slash(path), entry)
        is_file = os.path.isfile(full_path)
        translated_path = '{}{}'.format(self.append_slash(path).replace('/app/', 'lumafs://'), entry)
        contents.append({'name': entry, 'path': translated_path, 'type': 1 if is_file else 2, 'contents': None})

      res = {
          "path": path,
          "contents": contents,
          "type": 2
          }
    else:
      raise Exception('Invalid path')

    return jsonify(res)

  def append_slash(self, path):
    if not path.endswith('/'):
      return path + '/'

    return path

  def write_file(self, root, path, content):
    path = self.validate_path(root, path)

    print(content, flush=True)

    with open(path, 'w+') as f:
      f.write(content)

    return jsonify('ok')
