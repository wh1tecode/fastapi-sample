def user_info():
    return [
        {
            "$lookup": {
                "from": "user",
                "localField": "user.$id",
                "foreignField": "_id",
                "as": "account",
            }
        },
        {"$unwind": {"path": "$account"}},
        {
            "$project": {
                "id": {"$toString": "$account._id"},
                "first_name": "$account.first_name",
                "last_name": "$account.last_name",
                "phone_number": "$account.phone_number",
                "email_address": "$account.email_address",
                "avatar_image": "$account.avatar_image",
                "banner_image": "$account.banner_image",
                "username": "$account.username",
                "is_superuser": "$account.is_superuser",
                "scopes": "$account.scopes",
                "refresh_token": "$session.refresh_token",
                "created_date": {"$toLong": "$account.created_date"},
                "updated_date": {"$toLong": "$account.updated_date"},
            }
        },
        {"$unset": "_id"},
    ]
