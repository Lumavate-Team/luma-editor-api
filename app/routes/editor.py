from lumavate_service_util import lumavate_route, RequestType, SecurityType, lumavate_blueprint
from flask import Blueprint, request, Response
import behavior

editor_blueprint = Blueprint("editor_blueprint", __name__)

@lumavate_blueprint.route('/<string:ic>/<string:wt>/editor/read', methods=['GET'])
def read(ic, wt):
  for line in tailer.follow(open('test.txt')):
    yield ','.join(line) + '\n'

  return behavior.EditorBehavior().read(request.args.get('path'))

@lumavate_blueprint.route('/<string:ic>/<string:wt>/editor/stat', methods=['GET'])
def stat(ic, wt):
  return behavior.EditorBehavior().stat(request.args.get('path'))

@lumavate_blueprint.route('/<string:ic>/<string:wt>/editor/write', methods=['PUT'])
def write(ic, wt):
  return behavior.EditorBehavior().write_file(request.args.get('path'), request.get_json().get('content'))


@lumavate_blueprint.route('/logs', methods=['GET'])
def logs():
  print("here", flush=True)
  def generate():
    with open("/tmp/supervisord.log", "r") as logs:
      for line in logs:
        print(line, flush=True)
        yield line


  return Response(generate(), mimetype='text/plain')

