class SpotifyTrackError(Exception):
    """
    Base class for SpotifyTrack exceptions.
    """
    pass

class SpotifyTrackHTTPException(SpotifyTrackError):
    """
    Exception for SpotifyTrack HTTP errors.
    """
    def __init__(self, response, message=None):
        self.response = response
        self.status_code = response.status

        message = message or response.reason

        super().__init__('Status Code %s: %s' % (self.status_code, message))