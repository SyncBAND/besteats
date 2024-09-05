from rest_framework.exceptions import APIException


class RestaurantVoteException(APIException):
    status_code = 400
    default_detail = (
        "You have run out of votes, please try again tomorrow"
    )


class RestaurantUnvoteException(APIException):
    status_code = 400
    default_detail = (
        "User has not cast a vote yet"
    )
