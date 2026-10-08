class GameError(Exception):
    """A game rule was violated. Routers turn it into an HTTP error:
    {"detail": message, "code": code} with the given status."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def not_found(what: str) -> GameError:
    return GameError(404, "not_found", f"{what} not found")
