from flask import Blueprint, request, Response, send_file
from behavior import EditorBehavior, PackageBehavior, FSException
import time

editor_blueprint = Blueprint("editor_blueprint", __name__)

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs', defaults={'path': '', 'root': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>/<path:path>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def editor_core(ic, wt, root, path):
  b = EditorBehavior()
  methods = {
      'GET': b.read,
      'PUT': b.write,
      'POST': b.create,
      'DELETE': b.delete
      }

  return methods[request.method](root, path)

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/download/application.zip', methods=['GET'])
def download_src(ic, wt):
  data = EditorBehavior().get_app_archive()
  return send_file(data, attachment_filename='application.zip', as_attachment=True, mimetype='application/zip')

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/package', methods=['POST', 'GET'])
def project_packages(ic, wt):
  b = PackageBehavior()
  if request.method == 'POST':
    return b.package_install()

  if request.method == 'GET':
    return b.get_packages()

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/restart/app', methods=['POST'])
def restart_process(ic, wt):
  b = PackageBehavior()
  return b.restart_process()

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/logs', methods=['GET'])
def logs(ic, wt):
  tail_length = request.args.get('tail')
  resp = Response(follow(tail_length), mimetype='text/plain')
  resp.headers['X-Accel-Buffering'] = 'no'
  return resp

def follow(tail):
  if not tail:
    tail = 100
  try:
    tail_length = int(f'-{tail}')
  except:
    raise FSException("'tail' arg must be an int")

  with open('/logs/app.log', 'r') as file:
    line = ''
    ct = 0
    while True:
      time.sleep(0.01)
      ct += 1
      if ct > 4500:
        ct = 0
        yield " "

      lines = file.readlines()
      tail = lines[tail_length:]
      for tmp in tail:
        if tmp is not None:
          line += tmp
          if line.endswith("\n"):
            yield line
            line = ''
            ct = 0
        else:
          time.sleep(0.1)
