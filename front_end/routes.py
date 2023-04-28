from typing import Dict, List
from flask import jsonify, request, current_app
from front_end import bp
from back_end import ProfileHandler, ConfigurationHandler
from flask_jwt_extended import jwt_required, get_jwt
from capif import CapifHandler

def validate(data: Dict, expected: List[str]):
    keys = data.keys()
    missing = []
    for key in expected:
        if key not in keys:
            missing.append(key)
    return missing

def isAuthorized() -> bool:
    if current_app.config["CAPIF_SECURITY_ENABLED"]:
        # If the token exists, but is invalid, @jwt_required will handle the error. This can be confirmed by commenting
        # @jwt_required, importing verify_jwt_in_request and adding a breakpoint before processing the request. Calling
        # verify_jwt_in_request with a too short Bearer will raise "Not enough segments", the same as when using
        # @jwt_required directly.

        return len(get_jwt()) != 0
    else:
        return True


@bp.route('/profile', methods=['GET'])
@jwt_required(optional=True)
def profile():
    if not isAuthorized(): return "403 Forbidden", 403

    name = request.args.get('name', None)
    if name is None:
        return jsonify(
            {'profiles': ProfileHandler.GetProfileNames()}
        )
    else:
        return jsonify(
            {name: ProfileHandler.GetProfileData(name)}
        )

@bp.route('/apply', methods=['POST'])
@jwt_required(optional=True)
def apply():
    if not isAuthorized(): return "403 Forbidden", 403

    data = request.json

    missing = validate(data, ['profile', 'identifier', 'overrides'])
    if len(missing) > 0:
        return jsonify({
            'message': 'Bad Request',
            'detail': f'Payload is missing the following fields: {missing}'
        }), 400

    success, text = ConfigurationHandler.Add(data['identifier'], data['profile'], data['overrides'])
    if success:
        return jsonify({
            'message': 'Success', 'token': text
        }), 200
    else:
        return jsonify({
            'message': 'Request Failed', 'detail': text
        }), 400

@bp.route('/clear', methods=['POST'])
@jwt_required(optional=True)
def clear():
    if not isAuthorized(): return "403 Forbidden", 403

    data = request.json

    missing = validate(data, ['identifier', 'token'])
    if len(missing) > 0:
        return jsonify({
            'message': 'Bad Request',
            'detail': f'Payload is missing the following fields: {missing}'
        }), 400

    success, text = ConfigurationHandler.Remove(data['identifier'], data['token'])
    if success:
        return jsonify({'message': text}), 200
    else:
        return jsonify({
            'message': 'Request Failed', 'detail': text
        }), 400