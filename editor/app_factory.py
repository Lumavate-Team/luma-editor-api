from flask import Flask, jsonify, send_from_directory, g
import os

def create_app(options=None):
    app = Flask(__name__)
    app.config.from_envvar('APP_SETTINGS')
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app
