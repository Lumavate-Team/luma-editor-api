from lumavate_service_util import lumavate_route, RequestType, SecurityType
from flask import request
import behavior


@lumavate_route('/hello-world/data', ['GET'], RequestType.api, [SecurityType.jwt])
def read():
  return behavior.HelloWorldBehavior().get_data()

@lumavate_route('/new/route', ['GET'], RequestType.api, [SecurityType.jwt])
def new():
  print("hello", flush=True)
  return behavior.HelloWorldBehavior().get_data()

@lumavate_route('/newer/route', ['GET'], RequestType.api, [SecurityType.jwt])
def newer():
  return behavior.HelloWorldBehavior().get_data()

@lumavate_route('/third/route', ['GET'], RequestType.api, [SecurityType.jwt])
def third():
  return behavior.HelloWorldBehavior().get_data()
