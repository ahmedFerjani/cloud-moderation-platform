"""Application-specific exception types used across Lambda handlers."""

class APPError(Exception):

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ):

        self.code = code
        self.message = message
        self.status_code = status_code

        super().__init__(message)
