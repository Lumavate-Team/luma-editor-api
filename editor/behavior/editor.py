from flask import jsonify, request
from pathlib import Path
from app import app
import shutil
import os
import re

class EditorBehavior():
  def __init__(self, data=None, args=None):
    self.project_config = app.config['DIR_STRUCT']

  def get_data(self, override_data=None):
    if override_data:
      return override_data

    if self.data:
      return self.data

    return request.get_json(force=True)

  def get_info(self):
    return jsonify(self.project_config)

  def set_paths(self, request_root, request_path, validate_real_path=True):
    real_root = self.project_config.get(request_root)
    if not real_root:
      raise NotFoundException("Root does not exist", payload={"root": request_root})

    real_path, editor_path = self.format_paths(request_root, real_root, request_path)

    if validate_real_path and not os.path.exists(real_path):
      raise NotFoundException("Path does not exist", payload={"path": request_path})

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
      raise NotFoundException("Invalid path", payload={"path": self.editor_path})

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
      raise NotFoundException("Invalid path", payload={"path": editor_path})

    if not raw:
      return jsonify(res)
    else:
      return res

  def create(self, root, path):
    self.set_paths(root, path, validate_real_path=False)

    # Can't overwite root path
    if not path:
      raise ValidationException("Can't overwrite or rename the root path")

    # Determine if this is a "move" request or a "create"
    action = request.args.get('action')
    dest = request.args.get('dest')
    if action and dest and action == 'move':
      return self.move(root, path, dest)

    # This is a "create" request
    if os.path.exists(self.real_path):
      raise ValidationException("Path already exists", payload={"path": self.editor_path})

    try:
      # Try to parse the request data
      self.data = self.get_data()
    except Exception as e:
      raise ValidationException("Failed to parse request body as JSON", payload={'path': path, 'exception': str(e)})

    try:
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
      raise FSException("Error creating the file or directory", payload={'type': self.data.get('type'), 'path': path, 'exception': str(e)})

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

  def move(self, request_root, old_path, new_path):
    try:
      real_root = self.project_config.get(request_root)
      if not real_root:
        raise NotFoundException("Root does not exist", payload={"root": request_root})

      real_old_path, editor_old_path = self.format_paths(request_root, real_root, old_path)

      # new_path should begin with the project root. Parse that out and make sure
      # it matches the request_root
      match = re.search('^\/(?P<root>[^\/]+)(?P<path>.*)', new_path)
      if not match:
        raise ValidationException("New path isn't a valid path format", payload={'path': new_path})

      new_path_root = match.group('root')
      if new_path_root != request_root:
        raise ValidationException("Destination path root '{}' doesn't match the request root '{}'".format(new_path_root, request_root), payload={'path': new_path})

      # Replace the first occurrence of the root in the new path
      new_path = new_path.replace('/{}/'.format(new_path_root), '', 1)

      real_new_path, editor_new_path = self.format_paths(request_root, real_root, new_path)

      if not os.path.exists(real_old_path):
        raise NotFoundException("Path does not exist", payload={"path": editor_old_path})

      shutil.move(real_old_path, real_new_path)

      return jsonify('ok')
    except Exception as e:
      if isinstance(e, FSException):
        raise

      raise FSException("Error moving path", payload={'path': editor_old_path, 'exception': str(e)})

  def write(self, root, path):
    self.set_paths(root, path, validate_real_path=False)

    try:
      content = request.get_json().get('content')
      # Allow empty content, just not None content
      if content is None:
        raise ValidationException("'content' is required", payload={'path': self.editor_path, 'exception': str(e)})

    except Exception as e:
      raise ValidationException("Error parsing request content", payload={'path': self.editor_path, 'exception': str(e)})

    try:
      with open(self.real_path, 'w') as f:
        f.write(content)

      return jsonify('ok')
    except Exception as e:
      raise FSException("Error writing to path", payload={'path': self.editor_path, 'exception': str(e)})


class FSException(Exception):
  def __init__(self, message, payload=None, status_code=500):
    Exception.__init__(self)
    self.message = message
    self.payload = payload
    self.status_code = status_code

  def to_dict(self):
    rv = dict(self.payload or ())
    rv.update({'error': self.message})
    return jsonify(rv), self.status_code

class NotFoundException(FSException):
  def __init__(self, message, payload=None):
    FSException.__init__(self, message, payload, 404)

class ValidationException(FSException):
  def __init__(self, message, payload=None):
    FSException.__init__(self, message, payload, 400)
