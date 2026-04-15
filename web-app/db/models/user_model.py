def make_user(fridge_id, user_name, user_email, user_password_hash):
    return {
        "fridge_id": fridge_id,
        "user_name": user_name,
        "user_email": user_email,
        "user_password_hash": user_password_hash
    }
