#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyBroadException
try:
    import eventlet
    eventlet.monkey_patch(all=True)
except:
    pass

import logging
import logging.config
import eventlet.wsgi
import os
import sqlalchemy_utils
import yaml
from thorn.models import db, User
from flask import Flask, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import get_locale, Babel
from flask_cors import CORS
from flask_restful import Api, abort

from thorn.permission_api import PermissionListApi
from thorn.user_api import UserListApi

sqlalchemy_utils.i18n.get_locale = get_locale

app = Flask(__name__)

babel = Babel(app)

logging.config.fileConfig('logging_config.ini')

app.secret_key = 'l3m0n4d1_thorn'
# Flask Admin 
admin = Admin(app, name='Lemonade', template_mode='bootstrap3')

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

mappings = {
    '/permissions': PermissionListApi,
    '/users': UserListApi,
#    '/dashboards/<int:dashboard_id>': DashboardDetailApi,
#    '/visualizations/<int:job_id>/<task_id>': VisualizationDetailApi,
#    '/visualizations': VisualizationListApi,
}
for path, view in list(mappings.items()):
    api.add_resource(view, path)


@babel.localeselector
def get_locale():
    return request.args.get('lang', 'en')


def main(is_main_module):
    config_file = os.environ.get('THORN_CONFIG')

    os.chdir(os.environ.get('THORN_HOME', '.'))
    logger = logging.getLogger(__name__)
    if config_file:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)['thorn']

        app.config["RESTFUL_JSON"] = {"cls": app.json_encoder}

        server_config = config.get('servers', {})
        app.config['SQLALCHEMY_DATABASE_URI'] = server_config.get(
            'database_url')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 240

        app.config.update(config.get('config', {}))
        app.config['THORN_CONFIG'] = config

        db.init_app(app)

        port = int(config.get('port', 5000))
        logger.debug('Running in %s mode', config.get('environment'))

        if is_main_module:
            if config.get('environment', 'dev') == 'dev':
                admin.add_view(ModelView(User, db.session))
                app.run(debug=True, port=port)
            else:
                eventlet.wsgi.server(eventlet.listen(('', port)), app)
    else:
        logger.error('Please, set THORN_CONFIG environment variable')
        exit(1)


main(__name__ == '__main__')
