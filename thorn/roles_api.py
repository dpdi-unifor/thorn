# -*- coding: utf-8 -*-}
from thorn.app_auth import requires_auth
from flask import request, current_app, g as flask_globals
from flask_restful import Resource
from sqlalchemy import or_

import math
import logging
from thorn.schema import *
from flask_babel import gettext

log = logging.getLogger(__name__)

# region Protected\s*
# endregion
def translate_validation(validation_errors):
    for field, errors in list(validation_errors.items()):
        validation_errors[field] = [gettext(error) for error in errors]
    return validation_errors


class RolesListApi(Resource):
    """ REST API for listing class Roles """

    def __init__(self):
        self.human_name = gettext('Roles')

    @requires_auth
    def get(self):
        if request.args.get('fields'):
            only = [f.strip() for f in request.args.get('fields').split(',')]
        else:
            only = ('id', ) if request.args.get(
                'simple', 'false') == 'true' else None
        enabled_filter = request.args.get('enabled')
        if enabled_filter:
            roless = Roles.query.filter(
                Roles.enabled == (enabled_filter != 'false'))
        else:
            roless = Roles.query.all()

        page = request.args.get('page') or '1'
        if page is not None and page.isdigit():
            page_size = int(request.args.get('size', 20))
            page = int(page)
            pagination = roless.paginate(page, page_size, True)
            result = {
                'data': RolesListResponseSchema(
                    many=True, only=only).dump(pagination.items),
                'pagination': {
                    'page': page, 'size': page_size,
                    'total': pagination.total,
                    'pages': int(math.ceil(1.0 * pagination.total / page_size))}
            }
        else:
            result = {
                'data': RolesListResponseSchema(
                    many=True, only=only).dump(
                    roless)}

        if log.isEnabledFor(logging.DEBUG):
            log.debug(gettext('Listing %(name)s', name=self.human_name))
        return result


class RolesDetailApi(Resource):
    """ REST API for a single instance of class Roles """
    def __init__(self):
        self.human_name = gettext('Roles')

    @requires_auth
    def get(self, roles_id):

        if log.isEnabledFor(logging.DEBUG):
            log.debug(gettext('Retrieving %s (id=%s)'), self.human_name,
                      roles_id)

        roles = Roles.query.get(roles_id)
        return_code = 200
        if roles is not None:
            result = {
                'status': 'OK',
                'data': [RolesItemResponseSchema().dump(
                    roles).data]
            }
        else:
            return_code = 404
            result = {
                'status': 'ERROR',
                'message': gettext(
                    '%(name)s not found (id=%(id)s)',
                    name=self.human_name, id=roles_id)
            }

        return result, return_code
