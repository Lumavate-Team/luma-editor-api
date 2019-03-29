from lumavate_properties import Properties, Components
from lumavate_service_util import LumavateMockRequest, set_lumavate_request_factory, DevMock, LumavateRequest
from lumavate_token import AuthToken
import json
import os

class RequestDevMock(DevMock):
  def get_auth_token(self):
    t = super().get_auth_token()
    t.auth_url = 'http://{}:5005/ic/saml/'.format(os.environ.get('DOCKER_IP'))
    t.namespace = 'abc'
    return t

  def get_property_data(self):
    sd = super().get_property_data()
    return sd


  def get_auth_data(self):
    return {
      'roles': [
        'Super Admins'
      ],
      'status': 'active',
      'user': 'ic~saml!user!1'
    }
