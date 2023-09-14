from dataclasses import dataclass


@dataclass
class SqlSettings:
    WIPED_PASSWORD = "WIPED"
    DEFAULT_DATABASE = "bcloud"
    DEFAULT_DATABASE_DEV = "bcloud_dev"

    host: str
    port: int
    username: str
    password: str
    database: str

    def wipe(self):
        self.password = self.WIPED_PASSWORD

    @property
    def is_wiped(self):
        return self.password == self.WIPED_PASSWORD
    
    @classmethod
    def default_database(cls, production: bool):
        if production:
            return cls.DEFAULT_DATABASE
        else:
            return cls.DEFAULT_DATABASE_DEV
        
    @property
    def is_sqlite(self):
        return self.host.endswith(".sqlite")
