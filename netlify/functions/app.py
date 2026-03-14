from app import create_app
import awsgi


flask_app = create_app("production")


def handler(event, context):
    return awsgi.response(flask_app, event, context)

