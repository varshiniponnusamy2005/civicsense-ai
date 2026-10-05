from database import complaints_collection
from bson import ObjectId


def create_complaint(complaint_data):
    result = complaints_collection.insert_one(
        complaint_data
    )

    return str(
        result.inserted_id
    )


def get_complaint_by_id(complaint_id):

    try:
        return complaints_collection.find_one({
            "_id": ObjectId(
                complaint_id
            )
        })

    except Exception:
        return None