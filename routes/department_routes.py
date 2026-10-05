from flask import Blueprint, request, jsonify

from models.department_model import (
    create_department,
    get_department_by_name,
    get_all_departments
)


department_bp = Blueprint(
    "department",
    __name__,
    url_prefix="/api/departments"
)


@department_bp.route("/", methods=["POST"])
def add_department():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Department data is required"
        }), 400

    name = data.get("name")

    if not name:
        return jsonify({
            "message": "Department name is required"
        }), 400

    if get_department_by_name(name):
        return jsonify({
            "message": "Department already exists"
        }), 409

    department_id = create_department({
        "name": name,
        "email": data.get("email", ""),
        "phone": data.get("phone", "")
    })

    return jsonify({
        "message": "Department created successfully",
        "department_id": department_id
    }), 201


@department_bp.route("/", methods=["GET"])
def get_departments():
    departments = get_all_departments()

    for department in departments:
        department["_id"] = str(department["_id"])

    return jsonify(departments), 200