"""Container for methods that serve data to the apps."""


class DataServer:
    """Container for methods that serve data to the apps."""

    def __init__(self, db_file_path: str) -> None:
        """Inits with path to the SQLite db file.

        Parameters
        ----------
        db_file_path : str
            path to SQLite db file
        """
        self.db_file_path = db_file_path

    def say_hello(self):
        print(self.db_file_path)
