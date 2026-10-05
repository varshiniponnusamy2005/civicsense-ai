from database import departments_collection


def create_department(department_data):
    result = departments_collection.insert_one(department_data)
    return str(result.inserted_id)


def get_department_by_name(name):
    return departments_collection.find_one({
        "name": name
    })


def get_all_departments():
    return list(departments_collection.find())