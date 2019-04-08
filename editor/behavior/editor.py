from lumavate_service_util import RestBehavior
from flask import jsonify, request, g, app
from pathlib import Path
import shutil
import os

class EditorBehavior(RestBehavior):
  def __init__(self, data=None, args=None):
    self.project_config = {
      'app': '/app/',
      'lumavate_properties': '/python_packages/lumavate_properties/'
    }

    super().__init__(None)

  def get_info(self):
    return jsonify(self.project_config)

  def set_paths(self, request_root, request_path, validate_real_path=True):
    real_root = self.project_config.get(request_root)
    if not real_root:
      raise FSException("Root does not exist", payload={"root": request_root})

    real_path, editor_path = self.format_paths(request_root, real_root, request_path)

    if validate_real_path and not os.path.exists(real_path):
      raise FSException("Path does not exist", payload={"path": request_path})

    self.real_path = real_path
    self.editor_path = editor_path

  def append_slash(self, path):
    if not path.endswith('/'):
      return path + '/'

    return path

  def format_paths(self, req_root, real_root, path):
    if not req_root.startswith('/'):
      req_root = '/{}'.format(req_root)

    real_path = '{}{}'.format(self.append_slash(real_root), path)
    editor_path = '{}{}'.format(self.append_slash(req_root), path)
    return real_path, editor_path

  def format_real_path(self, root, path):
    req_root = self.project_config.get(root)

    if path:
      new_path = '{}{}'.format(req_root, path)
    else:
      new_path = req_root

    return new_path

  def stat(self, root, path):
    res = None
    if not root and not path:
      res = {
        'path': '/',
        'type': 2
      }
      return jsonify(res)

    self.set_paths(root, path)
    if os.path.isfile(self.real_path):
      res = {
          "path": self.editor_path,
          "type": 1
          }
    elif os.path.isdir(self.real_path):
      res = {
          "path": self.editor_path,
          "type": 2
          }
    else:
      raise FSException("Invalid path", payload={"path": self.editor_path})

    return jsonify(res)

  def get_project_config(self):
    res = {}
    conf = self.project_config
    for x in conf.keys():
      res[x] = self.read(x, "", raw=True)

    return res

  def read(self, root, req_path, raw=False):
    if 'stat' in request.args:
      return self.stat(root, req_path)

    res = None
    if not root and not req_path:
      contents = []
      for k in self.project_config.keys():
        contents.append({
          'path': '/' + k,
          'type': 2,
          'name': k
        })

      res = {
        "path": '/',
        "contents": contents,
        "type": 2
      }

      return jsonify(res)

    self.set_paths(root, req_path)
    if os.path.isfile(self.real_path):
      contents = Path(self.real_path).read_text()
      res = {
          "path": self.editor_path,
          "contents": contents,
          "type": 1
          }
    elif os.path.isdir(self.real_path):
      dir_contents = os.listdir(self.real_path)
      contents = []

      for entry in dir_contents:
        editor_full_path = '{}{}'.format(self.append_slash(self.editor_path), entry)
        is_file = os.path.isfile('{}{}'.format(self.append_slash(self.real_path), entry))
        contents.append({'name': entry, 'path': editor_full_path, 'type': 1 if is_file else 2, 'contents': None})

      res = {
          "path": self.editor_path,
          "contents": contents,
          "type": 2
          }
    else:
      raise FSException("Invalid path", payload={"path": editor_path})

    if not raw:
      return jsonify(res)
    else:
      return res

  def create(self, root, path):
    self.set_paths(root, path, validate_real_path=False)

    # Can't overwite root path
    if not path:
      raise FSException("Can't overwrite the root path")

    if os.path.exists(self.real_path):
      raise FSException("Path already exsist", payload={"path": self.editor_path})

    try:
      data = self.get_data()
      if data.get('type') == 'directory':
        os.makedirs(self.real_path)
      elif data.get('type') == 'file':
        file_name = path.split('/')[-1]
        file_path = '/'.join(path.split('/')[:-1])

        if not os.path.exists(self.format_real_path(root, file_path)):
          os.makedirs(self.format_real_path(root, file_path))
          open(self.real_path, 'a').close()
        else:
          open(self.real_path, 'a').close()

      return self.read(root, path)

    except Exception as e:
      raise FSException("Error creating the file or directory", payload={'type': self.get_data().get('type'), 'path': path, 'exception': str(e)})

  def delete(self, root, path):
    self.set_paths(root, path)

    try:
      if os.path.isfile(self.real_path):
        os.remove(self.real_path)
      elif os.path.isdir(self.real_path):
        shutil.rmtree(self.real_path)

      return jsonify('ok')
    except Exception as e:
      raise FSException("Error deleting path", payload={'path': self.editor_path, 'exception': str(e)})


  def write(self, root, path):
    self.set_paths(root, path, validate_real_path=False)

    try:
      content = request.get_json().get('content')
      # Allow empty content, just not None content
      if content is None:
        raise FSException("'content' is required", payload={'path': self.editor_path, 'exception': str(e)})

    except Exception as e:
      raise FSException("Error parsing request content", payload={'path': self.editor_path, 'exception': str(e)})

    try:
      with open(self.real_path, 'w') as f:
        f.write(content)

      return jsonify('ok')
    except Exception as e:
      raise FSException("Error writing to path", payload={'path': self.editor_path, 'exception': str(e)})


class FSException(Exception):
  def __init__(self, message, payload=None, status_code=400):
    Exception.__init__(self)
    self.message = message
    self.payload = payload
    self.status_code = status_code

  def to_dict(self):
    rv = dict(self.payload or ())
    rv['FSError'] = self.message
    return jsonify(rv), self.status_code

