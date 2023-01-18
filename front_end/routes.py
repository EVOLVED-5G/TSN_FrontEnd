from flask import jsonify, request
from front_end import bp
from back_end import ProfileHandler


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
