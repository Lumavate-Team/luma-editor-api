from lumavate_service_util import lumavate_blueprint
from flask import Blueprint, request
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
