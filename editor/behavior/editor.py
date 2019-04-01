from lumavate_service_util import RestBehavior
from flask import jsonify, request, g
from pathlib import Path
import shutil
import os

class EditorBehavior(RestBehavior):
  def __init__(self, data=None, args=None):
    self.project_config = {
        'widget': '/app/',
        'dep': '/other_path/'
        }

    super().__init__(None)

  def get_info(self):
    return jsonify(self.project_config)

  def append_slash(self, path):
    if not path.endswith('/'):
      return path + '/'

    return path

  def format_real_path(self, root, path):
    req_root = self.project_config.get(root)

    if path:
      new_path = '{}{}'.format(req_root, path)
    else:
      new_path = req_root

    return new_path

  def format_editor_path(self, root, req_path):
    editor_path = '{}{}'.format(self.append_slash(root), req_path)

    if os.path.isdir(self.format_real_path(root, req_path)):
      return self.append_slash(editor_path)
    else:
      return editor_path

  def validate_path(self, root, path):
    req_root = self.project_config.get(root)
    if not req_root:
      raise Exception('Path does not exsist')

    new_path = self.format_real_path(root, path)

    if not os.path.exists(new_path):
      raise Exception('Path does not exsist')

    return new_path

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

  def read(self, root, req_path):
    if 'stat' in request.args:
      return self.stat(root, req_path)

    path = self.validate_path(root, req_path)
    editor_path = self.format_editor_path(root, req_path)

    res = None
    if os.path.isfile(path):
      contents = Path(path).read_text()
      res = {
          "path": editor_path,
          "contents": contents,
          "type": 1
          }
    elif os.path.isdir(path):
      dir_contents = os.listdir(path)
      contents = []

      for entry in dir_contents:
        full_path = '{}{}'.format(editor_path, entry)
        is_file = os.path.isfile(full_path)
        contents.append({'name': entry, 'path': full_path, 'type': 1 if is_file else 2, 'contents': None})

      res = {
          "path": editor_path,
          "contents": contents,
          "type": 2
          }
    else:
      raise Exception('Invalid path')

    return jsonify(res)

  def create(self, root, path):
    req_root = self.project_config.get(root)
    if not req_root:
      raise Exception('Root path does not exsist')

    # Can't overwite root path
    if not path:
      raise Exception('Path already exsists')
    else:
      new_path = self.format_real_path(root, path)

    if os.path.exists(new_path):
      raise Exception('Path already exsists')

    try:
      data = self.get_data()
      if data.get('type') == 'directory':
        os.makedirs(new_path)
      elif data.get('type') == 'file':
        file_name = path.split('/')[-1]
        file_path = '/'.join(path.split('/')[:-1])

        if not os.path.exists(self.format_real_path(root, file_path)):
          os.makedirs(self.format_real_path(root, file_path))
          open(new_path, 'a').close()
        else:
          open(new_path, 'a').close()

      return self.read(root, path)

    except Exception as e:
      return jsonify({"status": 'failed'})

  def delete(self, root, path):
    self.validate_path(root, path)
    path = self.format_real_path(root, path)

    if os.path.isfile(path):
      os.remove(path)
    elif os.path.isdir(path):
      shutil.rmtree(path)

    return jsonify('ok')

  def write(self, root, path):
    path = self.validate_path(root, path)

    with open(path, 'w') as f:
      f.write(content)

    return jsonify('ok')
