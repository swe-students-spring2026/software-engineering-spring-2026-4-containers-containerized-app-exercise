TABLE User
user_id
user_name
user_email
user_password_hash
user_owned_fridge
# P2: User -> Multiple Fridge? Rich dudes having multiple homes?

TABLE Fridge
fridge_id
owner_ids[]
item_ids[]
# P2: Permission?

TABLE Item
item_id
item_name
item_added_date
item_expiry_date
item_confidence
