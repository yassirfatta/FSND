import os
import sys
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-2h6vkhff.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Movies'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    # print('hi', auth)
    if not auth:
        print('AuthEror 1')
        raise AuthError({
            'code' : 'authorization_header_missing',
            'description' : 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    print('hello', parts)
    if parts[0] != 'Bearer':
        print('AuthEror 2')
        raise AuthError({
            'code' : 'invalid_header',
            'description' : 'Authorization header must start with "bearer".'
        }, 401)

    elif len(parts) == 1:
        print('AuthEror 3')
        raise AuthError({
            'code' : 'invalid_header',
            'description' : 'Token not found.'
        }, 401)
        
    elif len(parts) > 2:
        print('AuthEror 4')
        raise AuthError({
            'code' : 'invalid_header',
            'description' : 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token

#    raise Exception('Not Implemented')

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        print('AuthEror 5')
        raise AuthError({
            'code' : 'invalid_claims',
            'description' : 'Permissions not included in JWT.'
        }, 401)
    if permission not in payload['permissions']:
        print('AuthEror 6')
        raise AuthError({
            'code' : 'unauthorized',
            'description' : 'Permissions not found.'
        }, 403)
    return True

    # raise Exception('Not Implemented')

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        print('AuthEror 7')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            print('AuthEror 8')
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            print('AuthEror 9')
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            print('AuthEror 10')
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    print('AuthEror 11')        
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

    # raise Exception('Not Implemented')

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

# create and configure the app

# def create_app(test_config=None):
app = Flask(__name__)
CORS(app)
setup_db(app)

# ROUTES
'''
    GET /movies
'''
@app.route('/movies', methods = ['GET'])
@requires_auth('get:movies')
def get_movies(payload):
    print(payload)
    movies = []
    try:
        movies = Movie.query.name
        if len(movies) == 0:
            abort(404)
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "movies": movies}), 200

'''
    GET /actors
'''
@app.route('/actors', methods = ['GET'])
@requires_auth('get:actors')
def get_actors(payload):
    print(payload)
    actors = []
    try:
        actors = Actor.query.name
        if len(actors) == 0:
            abort(404)
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "actors": actors}), 200

'''
    POST /movies
'''
@app.route('/movies', methods = ['POST'])
@requires_auth('post:movies')
def post_movies(payload):
    print(payload)
    movie = []
    data = request.get_json()
    try:
        movie = Movie(
            name=data['name'],
            gente=data['genre']
        )
        movie.insert()
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "movies": movie}), 200

'''
    POST /actors
'''
@app.route('/actors', methods = ['POST'])
@requires_auth('post:actors')
def post_actors(payload):
    print(payload)
    actor = []
    data = request.get_json()
    try:
        actor = Actor(
            name=data['name'],
            gender=data['gender']
        )
        actor.insert()
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "actors": actor}), 200


'''
    PATCH /movies/<id>
'''
@app.route('/movies/<id>', methods = ['PATCH'])
@requires_auth('patch:movies')
def patch_movies(id, payload):
    print(payload)
    body = request.get_json()
    try:
        movie = Movie.query.filter(Movie.id == id)
        if movie is None:
            abort(404)
        movie.name = body.get('name')
        movie.genre = body.get('genre')
        movie.update()
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "movies": movie}), 200

'''
    PATCH /actors/<id>
'''
@app.route('/actors/<id>', methods = ['PATCH'])
@requires_auth('patch:actors')
def patch_actors(id, payload):
    print(payload)
    body = request.get_json()
    try:
        actor = Actor.query.filter(Actor.id == id)
        if actor is None:
            abort(404)
        actor.name = body.get('name')
        actor.gender = body.get('gender')
        actor.update()
    except:
        print(sys.exc_info())

    return jsonify({
        "success": True, 
        "actors": actor}), 200

'''
    DELETE /movies/<id>
'''
@app.route('/movies/<int:id>', methods = ['DELETE'])
@requires_auth('delete:movies')
def delete_movies(id, payload):
    print(payload)
    movie = Movie.query.get(id)
    if movie is None:
        abort(404)
    try:
        movie.delete()
    except:
        abort(422)

    return jsonify({
        "success": True, 
        "movies": movie}), 200

'''
    DELETE /actors/<id>
'''
@app.route('/actors/<int:id>', methods = ['DELETE'])
@requires_auth('delete:actors')
def delete_actors(id, payload):
    print(payload)
    actor = Actor.query.get(id)
    if actor is None:
        abort(404)
    try:
        actor.delete()
    except:
        abort(422)

    return jsonify({
        "success": True, 
        "actors": actor}), 200

# Error Handling
'''
Error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
Error handler for unavailable resources 
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
Error handler for AuthError
'''
@app.errorhandler(AuthError)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "invalid header"
    }), 400
    # return app

# app = create_app()
# if __name__ == '__main__':
#     app.run(host='http://127.0.0.1', port=5000, debug=True)