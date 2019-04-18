from lumavate_service_util import RestBehavior
from flask import jsonify

class HelloWorldBehavior(RestBehavior):
  def __init__(self):
    super().__init__(None)

  def get_data(self):
    return jsonify({'data': 10})
