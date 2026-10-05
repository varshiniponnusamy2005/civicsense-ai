import bcrypt

from database import users_collection


department_accounts = [
    {
        "name": "Public Works Department",
        "email": "varshiniknpm@gmail.com",
        "password": "Varsh#12",
        "role": "department",
        "department": "Public Works"
    },
    {
        "name": "Water Supply Department",
        "email": "santhipriyadarshini2@gmail.com",
        "password": "Priya#12",
        "role": "department",
        "department": "Water Supply"
    },
    {
        "name": "Electricity Department",
        "email": "dhivyadarshinipalanivel@gmail.com",
        "password": "Dhivya#12",
        "role": "department",
        "department": "Electricity"
    }
]


for account in department_accounts:

    existing_user = users_collection.find_one({
        "email": account["email"]
    })

    if existing_user:
        print(
            f"Account already exists: {account['email']}"
        )

        # Update existing department account
        hashed_password = bcrypt.hashpw(
            account["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        users_collection.update_one(
            {
                "email": account["email"]
            },
            {
                "$set": {
                    "name": account["name"],
                    "password": hashed_password,
                    "role": "department",
                    "department": account["department"]
                }
            }
        )

        print(
            f"Account password updated: {account['email']}"
        )

    else:

        hashed_password = bcrypt.hashpw(
            account["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        new_account = {
            "name": account["name"],
            "email": account["email"],
            "password": hashed_password,
            "role": "department",
            "department": account["department"]
        }

        users_collection.insert_one(new_account)

        print(
            f"Department account created: {account['email']}"
        )


print("Department account setup completed.")