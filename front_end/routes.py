from typing import Dict, List
from flask import jsonify, request
from front_end import bp
from back_end import ProfileHandler, ConfigurationHandler

def validate(data: Dict, expected: List[str]):
    keys = data.keys()
    missing = []
    for key in expected:
        if key not in keys:
            missing.append(key)
    return missing

@bp.route('/profile', methods=['GET'])
def profile():
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
def apply():
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
def clear():
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