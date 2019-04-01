from lumavate_service_util import lumavate_route, RequestType, SecurityType, lumavate_blueprint
from flask import Blueprint, request, Response
import behavior

editor_blueprint = Blueprint("editor_blueprint", __name__)

@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>', defaults={'path': ''}, methods=['GET', 'PUT'])
@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/fs/<string:root>/<path:path>', methods=['GET', 'PUT'])
def editor_core(ic, wt, root, path):
  b = behavior.EditorBehavior()
  if request.method == 'GET':
    if 'stat' in request.args:
      return b.stat(root, path)

    return b.read(root, path)

  if request.method == 'PUT':
    return b.write(root, path)

@lumavate_blueprint.route('/<string:ic>/<string:wt>/luma-editor/proj/info', methods=['GET'])
def info(ic, wt):
  return behavior.EditorBehavior().get_info()
