from flask import Flask, jsonify, send_from_directory, g
import os

def create_app(options=None):
    app = Flask(__name__)
    app.config.from_envvar('APP_SETTINGS')

    # apply any configuration override options
    if options is not None:
      for key, value in options.items():
        app.config[key] = value

    return app
