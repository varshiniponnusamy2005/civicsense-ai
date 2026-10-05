import bcrypt

from database import users_collection


# --------------------------------------------------
# CREATE USER
# --------------------------------------------------

def create_user(user_data):
    password = user_data.get("password")

    if password:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        user_data["password"] = (
            hashed_password.decode("utf-8")
        )

    result = users_collection.insert_one(
        user_data
    )

    return str(result.inserted_id)


# --------------------------------------------------
# GET USER BY EMAIL
# --------------------------------------------------

def get_user_by_email(email):
    if not email:
        return None

    return users_collection.find_one({
        "email": email.lower().strip()
    })


# --------------------------------------------------
# GET USER BY MOBILE
# --------------------------------------------------

def get_user_by_mobile(mobile):
    if not mobile:
        return None

    return users_collection.find_one({
        "mobile": mobile.strip()
    })


# --------------------------------------------------
# GET USER BY NAME
# --------------------------------------------------

def get_user_by_name(name):
    if not name:
        return None

    name = name.strip()

    return users_collection.find_one({
        "name": {
            "$regex": f"^{name}$",
            "$options": "i"
        }
    })


# --------------------------------------------------
# GET USER BY EMAIL / MOBILE / NAME
# --------------------------------------------------

def get_user_by_identifier(identifier):
    if not identifier:
        return None

    identifier = identifier.strip()

    # Try email
    if "@" in identifier:

        user = get_user_by_email(
            identifier
        )

        if user:
            return user

    # Try mobile
    user = get_user_by_mobile(
        identifier
    )

    if user:
        return user

    # Try name
    user = get_user_by_name(
        identifier
    )

    if user:
        return user

    return None


# --------------------------------------------------
# VERIFY PASSWORD
# --------------------------------------------------

def verify_password(
    password,
    hashed_password
):
    try:

        if not password:
            return False

        if not hashed_password:
            return False

        if not isinstance(
            hashed_password,
            str
        ):
            return False

        if not hashed_password.startswith(
            ("$2a$", "$2b$", "$2y$")
        ):
            return False

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except (
        ValueError,
        TypeError,
        UnicodeEncodeError
    ):
        return False


# --------------------------------------------------
# UPDATE PASSWORD
# --------------------------------------------------

def update_password(
    email,
    new_password
):
    if not email:
        return False

    if not new_password:
        return False

    try:

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        )

        hashed_password = (
            hashed_password.decode("utf-8")
        )

        result = users_collection.update_one(
            {
                "email": email.lower().strip()
            },
            {
                "$set": {
                    "password": hashed_password
                }
            }
        )

        return result.modified_count > 0

    except Exception as error:

        print(
            "Password update error:",
            error
        )

        return False