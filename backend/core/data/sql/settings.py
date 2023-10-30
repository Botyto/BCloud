from dataclasses import dataclass


@dataclass
class SqlSettings:
    WIPED_PASSWORD = "WIPED"

    connection_string: str
    
    def wipe(self):
        self.connection_string = self.WIPED_PASSWORD
