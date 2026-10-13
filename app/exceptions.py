class LBUserNotFound(Exception):
    """The listening provider could not find the username."""

class LBUnavailable(Exception):
    """The listening provider could not complete the request."""

class NoUserActivity(Exception):
    """No recent activity found on this user."""

class GuitarProfileInvalid(Exception):
    """The user's guitar profile is not valid."""

class AnalysisUnavailable(Exception):
    """The AI provider could not complete an analysis request."""


class InvalidAnalysisResponse(Exception):
    """The AI response does not contain a complete, valid analysis batch."""
