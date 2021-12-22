from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
	payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
	if message:
		payload['message'] = message
	response = jsonify(payload)
	# jsonify() function returns a Flask response object with a default status code of 200
	response.status_code = status_code
	# after response is created, set the status code to the correct one for the error
	return response

def bad_request(message):
	return error_response(400, message)