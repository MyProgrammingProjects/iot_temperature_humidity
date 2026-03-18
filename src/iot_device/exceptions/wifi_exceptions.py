class WifiConnectionException(Exception):
    def __init__(self, message, error_code=None):
        super().__init__(message)  # Call the base class constructor
        self.message = message
        self.error_code = error_code

    def __str__(self):
        """String representation of the exception."""
        if self.error_code:
            return f"MyCustomError: {self.message} (Error Code: {self.error_code})"
        else:
            return f"MyCustomError: {self.message}"