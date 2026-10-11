class LBUserNotFound(Exception):
    """The listening provider could not find the username."""

class LBUnavailable(Exception):
    """The listening provider could not complete the request."""

class NoUserActivity(Exception):
    """No recent activity found on this user."""

class GuitarProfileInvalid(Exception):
    """The user's guitar profile is not valid."""