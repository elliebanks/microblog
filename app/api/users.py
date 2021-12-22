from flask import jsonify, request, url_for, abort
from app import db
from app.models import User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/users/<int:id', methods=['GET'])
@token_auth.login_required
def get_user(id):
	return jsonify(User.query.get_or_404(id).to_dict())
	# get_or_404() method of the query object is a variant of the get() method
	# it returns the object with a given 'id' if it exists
	# but instead of returning None when the id does not exist, it aborts the request
	# and returns a 404 error to the client
	# advantage of get_or_404() over get() is that it removes the need
	# to check the result of the query, simplifying the logic in view functions


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
	return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(user.followers, page, per_page,
								   'api.get_followers', id=id)
	return jsonify(data)


@bp.route('/users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(user.followed, page, per_page,
								   'api.get_followed', id=id)
	return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
	data = request.get_json() or {}
	# request.get_json() method extracts the JSON from the request
	# and returns it as a Python structure
	if 'username' not in data or 'email' not in data or 'password' not in data:
		return bad_request('must include username, email, and password fields')
		# checks that mandatory fields are included (username, email, password)
	if User.query.filter_by(username=data['username']).first():
		return bad_request('please use a different username')
		# checks that username is not already in use
	if User.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
		# checks that email address is not already in use
	# once data validation is passed, create a user object and add to the db:
	user = User()
	user.from_dict(data, new_user=True)
	db.session.add(user)
	db.session.commit()
	response = jsonify(user.to_dict())
	response.status_code = 201
	# 201 status code used when a new entity has been created
	response.headers['Location'] = url_for('api.get_user', id=user.id)
	# HTTP protocol requires that a 201 response includes a Location header
	# that is set to the URL of the new resource
	return response

@bp.route('/users/<int:id>/', methods=['PUT'])
@token_auth.login_required
def update_user(id):
	if token_auth.current_user().id != id:
		abort(403)
	user = User.query.get_or_404(id)
		# this request receives a user id as a dynamic part of the URL
		# you can load the designated user or return a 404 error if user isn't found
	data = request.get_json() or {}
		# Validation of username/email fields are more complicated with this request
		# These fields are optional in this request, so I need to check that a field is present
		# Second, before checking if the username/email are already taken
		# need to validate that they are different from the current ones
	if 'username' in data and data['username'] != user.username and \
			User.query.filter_by(username=data['username']).first():
		return bad_request('please use a different username')
	if 'email' in data and data['email'] != user.email and \
			User.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
	user.from_dict(data, new_user=False)
	db.session.commit()
	return jsonify(user.to_dict())