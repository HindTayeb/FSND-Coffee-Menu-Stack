# -------------------------------------------------------------------------- #
# Imports
# -------------------------------------------------------------------------- #
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# -------------------------------------------------------------------------- #
# App Config.
# -------------------------------------------------------------------------- #

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# -------------------------------------------------------------------------- #
# Routes.
# -------------------------------------------------------------------------- #


@app.route('/drinks')
def get_drinks():
    try:
        drinks_list = Drink.query.all()
        if len(drinks_list) == 0:
            abort(404)
        drinks = [drink.short() for drink in drinks_list]
        return jsonify({
                'success': True,
                'drinks': drinks
        })
    except:
        abort(400)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks_list = Drink.query.all()
        if len(drinks_list) == 0:
            abort(404)
        drinks = [drink.long() for drink in drinks_list]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        drinks_list = Drink.query.all()
        if len(drinks_list) == 0:
            abort(404)
        drinks = [drink.long() for drink in drinks_list]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    try:
        drink = Drink.query.filter(
                Drink.id == id
        ).one_or_none()

        body = request.get_json()
        drink.title = body.get('title', None)
        drink.recipe = json.dumps(body.get('recipe', None))
        drink.update()
        drinks_list = Drink.query.all()
        if len(drinks_list) == 0:
            abort(404)
        drinks = [drink.long() for drink in drinks_list]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(
            Drink.id == id
        ).one_or_none()
        if drink is None:
            abort(404)
        id = drink.id
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)

# -------------------------------------------------------------------------- #
# Error Handling.
# -------------------------------------------------------------------------- #


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad Request"
                    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405


@app.errorhandler(500)
def Internal_server_error(error):
    return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error['code']
    }), 401
