from app_factory import create_app
import os

app = create_app()

from routes import editor_blueprint
app.register_blueprint(editor_blueprint)

import behavior
app.register_error_handler(behavior.FSException, behavior.FSException.to_dict)

if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
