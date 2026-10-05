from database import complaints_collection


def check_duplicate(description):
    existing_complaint = complaints_collection.find_one({
        "description": description
    })

    if existing_complaint:
        return {
            "is_duplicate": True,
            "duplicate_id": str(existing_complaint["_id"])
        }

    return {
        "is_duplicate": False,
        "duplicate_id": None
    }