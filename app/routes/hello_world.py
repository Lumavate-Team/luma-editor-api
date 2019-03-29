from lumavate_service_util import lumavate_route, RequestType, SecurityType, lumavate_blueprint
from flask import Blueprint, request, Response
import behavior

hello_world_blueprint = Blueprint("hello_world_blueprint", __name__)

@lumavate_blueprint.route('/hello-world/data', methods=['GET'])
def read():
  return behavior.HelloWorldBehavior().get_data()
