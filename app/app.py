from app_factory import create_app
import os

app = create_app()

rest_model_mapping = {}

from lumavate_service_util import lumavate_blueprint, CustomEncoder, icon_blueprint
app.json_encoder = CustomEncoder

from routes import *
app.register_blueprint(icon_blueprint)
app.register_blueprint(lumavate_blueprint)

from cron_jobs import hourly
app.cli.add_command(hourly)

@app.before_first_request
def init():
  if os.environ.get('DEV_MODE', 'False').lower() == 'true':
    import dev_mock
    from behavior import Discover
    dm = dev_mock.RequestDevMock(Discover().properties)

if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
