from lumavate_service_util import lumavate_blueprint, lumavate_route, SecurityType, RequestType
from flask import Blueprint, request, Response
import behavior

editor_blueprint = Blueprint("editor_blueprint", __name__)

@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs', defaults={'path': '', 'root': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'DELETE'])
@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>/<path:path>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def editor_core(ic, wt, root, path):
  b = behavior.EditorBehavior()
  methods = {
      'GET': b.read,
      'PUT': b.write,
      'POST': b.create,
      'DELETE': b.delete
      }

  return methods[request.method](root, path)


@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/logs', methods=['GET'])
def logs(ic, wt):
  return Response(follow(), mimetype='text/plain')

def follow():
  with open('/logs/app.log', 'r') as file:
    line = ''
    while True:
      tmp = file.readline()
      if tmp is not None:
        line += tmp
        if line.endswith("\n"):
          yield line
          line = ''
      else:
        time.sleep(0.1)
