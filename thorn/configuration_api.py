# -*- coding: utf-8 -*-}
from thorn.app_auth import requires_auth, requires_permission
from flask import request, current_app, g as flask_globals
from flask_restful import Resource
from sqlalchemy import or_

import math
import logging
from thorn.schema import *
from flask_babel import gettext

log = logging.getLogger(__name__)

# region Protected\s*
# endregion\w*


class ConfigurationListApi(Resource):
    """ REST API for listing class Configuration """

    def __init__(self):
        self.human_name = gettext('Configuration')

    @requires_auth
    @requires_permission('ADMINISTRATOR')
    def get(self):
        if request.args.get('fields'):
            only = [f.strip() for f in request.args.get('fields').split(',')]
        else:
            only = ('id', ) if request.args.get(
                'simple', 'false') == 'true' else None
        enabled_filter = request.args.get('enabled')
        if enabled_filter:
            configurations = Configuration.query.filter(
                Configuration.enabled == (enabled_filter != 'false'))
        else:
            configurations = Configuration.query

        page = request.args.get('page') or '1'
        if page is not None and page.isdigit():
            page_size = int(request.args.get('size', 20))
            page = int(page)
            pagination = configurations.paginate(page, page_size, True)
            result = {
                'data': ConfigurationListResponseSchema(
                    many=True, only=only).dump(pagination.items),
                'pagination': {
                    'page': page, 'size': page_size,
                    'total': pagination.total,
                    'pages': int(math.ceil(1.0 * pagination.total / page_size))}
            }
        else:
            result = {
                'data': ConfigurationListResponseSchema(
                    many=True, only=only).dump(
                    configurations)}

        if log.isEnabledFor(logging.DEBUG):
            log.debug(gettext('Listing %(name)s', name=self.human_name))
        return result

    @requires_auth
    @requires_permission('ADMINISTRATOR')
    def patch(self):
        result = {'status': 'ERROR', 'message': gettext('Insufficient data.')}
        return_code = 404

        if log.isEnabledFor(logging.DEBUG):
            log.debug(gettext('Updating %s'), self.human_name)
        if request.json:
            request_schema = ConfigurationCreateRequestSchema( many=True)
            # Ignore missing fields to allow partial updates
            form = request_schema.load(request.json, partial=True)
            response_schema = ConfigurationItemResponseSchema()
            if not form.errors:
                try:
                    configurations = []
                    for config in form.data:
                        configurations.append(db.session.merge(config))
                    db.session.commit()
                    return_code = 200
                    result = {
                        'status': 'OK',
                        'message': gettext(
                            '%(n)s was updated with success!', n=self.human_name),
                        'data': [response_schema.dump(
                            configurations, many=True).data]
                    }
                except Exception as e:
                    result = {'status': 'ERROR',
                              'message': gettext("Internal error")}
                    return_code = 500
                    if current_app.debug:
                        result['debug_detail'] = str(e)
                    db.session.rollback()
            else:
                result = {
                    'status': 'ERROR',
                    'message': gettext('Invalid data for %(name)s (id=%(id)s)',
                                       name=self.human_name,
                                       id=configuration_id),
                    'errors': form.errors
                }
        return result, return_code
