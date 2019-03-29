from lumavate_service_util import lumavate_route, RequestType, SecurityType, lumavate_blueprint
from flask import Blueprint, request, Response
import behavior

editor_blueprint = Blueprint("editor_blueprint", __name__)

@lumavate_blueprint.route('/<string:ic>/<string:wt>/editor/<path:path>', methods=['GET', 'PUT'])
def read(ic, wt, path):
  b = behavior.EditorBehavior()
  if request.method == 'GET':
    if 'stat' in request.args:
      return b.stat(path)

    return b.read(path)

  if request.method == 'PUT':
    return b.write(path)
