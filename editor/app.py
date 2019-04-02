from flask_sqlalchemy import SQLAlchemy
from app_factory import create_app
import os

app = create_app()
db = SQLAlchemy(app)

rest_model_mapping = {}

from lumavate_service_util import lumavate_blueprint, CustomEncoder, icon_blueprint
app.json_encoder = CustomEncoder

from routes import *
app.register_blueprint(icon_blueprint)
app.register_blueprint(lumavate_blueprint)

import behavior
app.register_error_handler(behavior.FSException, behavior.FSException.to_dict)


if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
