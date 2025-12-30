from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError

def validate_body(model):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                json_data = request.get_json()
                if json_data is None:
                    return jsonify({
                        "error": "Invalid JSON body"
                    }), 400

                validated_data = model(**json_data)
                kwargs["body"] = validated_data

            except ValidationError as e:
                return jsonify({
                    "error": "Validation failed",
                    "details": e.errors()
                }), 400

            return fn(*args, **kwargs)
        return wrapper
    return decorator
