from lumavate_service_util import RestBehavior
from flask import jsonify, request, g
from pathlib import Path
import os

class EditorBehavior(RestBehavior):
  def __init__(self):
    super().__init__(None)

  def stat(self, path):
    if not path:
      raise Exception('Invalid path')

    path = path.replace('lumafs://chronos/', '/app/')
    print(path, flush=True)

    # Need to lock this down to only what's in their 'code' dir
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

  def read(self, path):
    if not path:
      raise Exception('Invalid path')

    path = path.replace('lumafs://chronos/', '/app/')
    print('====================', flush=True)
    print(path, flush=True)
    print('====================', flush=True)

    # Need to lock this down to only what's in their 'code' dir
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

  def write_file(self, path, content):
    if not content:
      raise Exception('Invalid content')

    print(content, flush=True)
    if not path:
      raise Exception('Invalid path')

    path = path.replace('lumafs://chronos/', '/app/')

    with open(path, 'w+') as f:
      f.write(content)

    return jsonify('ok')
