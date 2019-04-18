from flask import Blueprint, request, Response
import behavior
import time

editor_blueprint = Blueprint("editor_blueprint", __name__)

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs', defaults={'path': '', 'root': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>/<path:path>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def editor_core(ic, wt, root, path):
  b = behavior.EditorBehavior()
  methods = {
      'GET': b.read,
      'PUT': b.write,
      'POST': b.create,
      'DELETE': b.delete
      }

  return methods[request.method](root, path)

@editor_blueprint.route('/<string:ic>/<string:wt>/luma-editor/logs', methods=['GET'])
def logs(ic, wt):
  resp = Response(follow(), mimetype='text/plain')
  resp.headers['X-Accel-Buffering'] = 'no'
  return resp

def follow():
  with open('/logs/app.log', 'r') as file:
    line = ''
    ct = 0
    while True:
      time.sleep(0.01)
      ct += 1
      if ct > 4500:
        ct = 0
        yield " "

      tmp = file.readline()
      if tmp is not None:
        line += tmp
        if line.endswith("\n"):
          yield line
          line = ''
          ct = 0
      else:
        time.sleep(0.1)
