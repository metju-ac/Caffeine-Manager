from flask import jsonify


def missing_arguments_response():
    return jsonify({"error_code": 400,
                    "error_text": "Missing one or more arguments"}), 400


def invalid_argument_response(argument: str):
    return jsonify({
        "error_code": 422,
        "error_text": f'Invalid {argument} value'
    }), 422


def conflict_response_non_unique_argument(class_name: str, non_unique_argument: str):
    return jsonify({
        "error_code": 409,
        "error_text": f'Could not create new {class_name} because there already exists '
                      f'{class_name} with this {non_unique_argument}'
    }), 409


def conflict_response_missing_referenced_object(missing_class: str, missing_id: int):
    return jsonify({
        "error_code": 409,
        "error_text": f'Could not process request because there is no {missing_class} with id = {missing_id}'
    }), 409
