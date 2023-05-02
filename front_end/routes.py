from typing import Dict, List
from flask import jsonify, request, current_app
from front_end import bp
from back_end import ProfileHandler, ConfigurationHandler
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timezone
from capif import CapifHandler


def validate(data: Dict, expected: List[str]):
    keys = data.keys()
    missing = []
    for key in expected:
        if key not in keys:
            missing.append(key)
    return missing

def checkAuthorized() -> (bool, [str | None]):
    if current_app.config["CAPIF_SECURITY_ENABLED"]:
        # If the token exists, but is invalid, @jwt_required will handle the error. This can be confirmed by commenting
        # @jwt_required, importing verify_jwt_in_request and adding a breakpoint before processing the request. Calling
        # verify_jwt_in_request with a too short Bearer will raise "Not enough segments", the same as when using
        # @jwt_required directly.

        invoker = get_jwt().get('sub', None)
        return invoker is not None, invoker
    else:
        return True, None

def handleLogging(invoker: str | None, response: str, status: int):
    time = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    uri = request.base_url
    method = request.method
    payload = request.json if request.is_json else {}

    with open('access.log', 'a', encoding='utf8') as log:
        log.write(f'{time}|{method}|{uri}|Invoker:"{invoker}"|Payload:"{payload}"|Response:"{response}"[{status}]')

    CapifHandler.MaybeLog()


@bp.route('/profile', methods=['GET'])
@jwt_required(optional=True)
def profile():
    isAuthorized, invokerId = checkAuthorized()

    if isAuthorized:
        name = request.args.get('name', None)
        if name is None:
            response = {'profiles': ProfileHandler.GetProfileNames()}
        else:
            response = {name: ProfileHandler.GetProfileData(name)}
        status = 200
    else:
        status = 403
        response = "403 Forbidden"

    handleLogging(invokerId, response, status)
    return jsonify(response), status

@bp.route('/apply', methods=['POST'])
@jwt_required(optional=True)
def apply():
    isAuthorized, invokerId = checkAuthorized()

    if isAuthorized:
        data = request.json

        missing = validate(data, ['profile', 'identifier', 'overrides'])
        if len(missing) > 0:
            status = 400
            response = {
                'message': 'Bad Request',
                'detail': f'Payload is missing the following fields: {missing}'
            }
        else:
            success, text = ConfigurationHandler.Add(data['identifier'], data['profile'], data['overrides'])
            if success:
                status = 200
                response = {
                    'message': 'Success',
                    'token': text
                }
            else:
                status = 400
                response = {
                    'message': 'Request Failed',
                    'detail': text
                }
    else:
        status = 403
        response = "403 Forbidden"


    # TODO: Use logging
    return response, status


@bp.route('/clear', methods=['POST'])
@jwt_required(optional=True)
def clear():
    isAuthorized, invokerId = checkAuthorized()

    if isAuthorized:
        data = request.json

        missing = validate(data, ['identifier', 'token'])
        if len(missing) > 0:
            status = 400
            response = {
                'message': 'Bad Request',
                'detail': f'Payload is missing the following fields: {missing}'
            }
        else:
            success, text = ConfigurationHandler.Remove(data['identifier'], data['token'])
            if success:
                status = 200
                response = {'message': text}
            else:
                status = 400
                response = {
                    'message': 'Request Failed',
                    'detail': text
                }
    else:
        status = 403
        response = "403 Forbidden"

    # TODO: Use logging
    return response, status
