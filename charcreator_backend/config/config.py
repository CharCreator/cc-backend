import os
import typing
import base64
import json
import bcrypt
import jwt


class DbConfig:
    def __init__(self, data: dict):
        self.host: str = data["host"]
        self.port: int = data["port"]
        self.user: str = data["login"]
        self.password: str = data["password"]
        self.database: str = data["name"]

    def to_save(self):
        return {
            "host": self.host,
            "port": self.port,
            "login": self.user,
            "password": self.password,
            "name": self.database,
        }


class JwtConfig:
    def __init__(self, data: dict):
        self.secret: bytes = base64.b64decode(data["secret"])
        self.algorithm: str = data["algorithm"]
        self.expiration: int = data["expiration"]

    def to_save(self):
        return {
            "secret": base64.b64encode(self.secret).decode("utf-8"),
            "algorithm": self.algorithm,
            "expiration": self.expiration,
        }


class Config:
    _instance: typing.Optional["Config"] = None
    initialized = False

    db: DbConfig
    bcrypt_salt: bytes
    jwt: JwtConfig
    mail_send_api: str
    mail_send_token: str
    frontend_url: str
    is_production: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.load_from_file("config.json")

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            self.__example_filler()
            self.__save_to_file(path)
            print(
                f"Config file not found. Example file created at {path}. Populate it and restart the app."
            )
            exit(1)

        with open(path, "r") as f:
            data = json.load(f)
        self.db = DbConfig(data["db"])
        self.bcrypt_salt: bytes = base64.b64decode(data["bcrypt_salt"])
        self.jwt = JwtConfig(data["jwt"])
        self.mail_send_api: str = data["mail_send_api"].rstrip("/")
        self.mail_send_token: str = data["mail_send_token"]
        self.frontend_url: str = data.get(
            "frontend_url", "http://localhost:3000"
        ).rstrip("/")
        self.is_production = data.get("is_production", False)
        self.initialized = True

    def __example_filler(self):
        import bcrypt
        import os

        self.db = DbConfig(
            {
                "host": "cc-database",
                "port": 5432,
                "login": os.environ["POSTGRES_USER"],
                "password": os.environ["POSTGRES_PASSWORD"],
                "name": os.environ["POSTGRES_DB"],
            }
        )
        self.bcrypt_salt = bytes(bcrypt.gensalt(), encoding="utf-8")
        self.jwt = JwtConfig(
            {
                "secret": base64.b64encode(os.urandom(32)),
                "algorithm": "HS256",
                "expiration": 7 * 24 * 60 * 60,
            }
        )
        self.mail_send_api: str = "https://mailapi.charcreator.ru/"
        self.mail_send_token: str = "KEY"
        self.frontend_url: str = "https://charcreator.ru/"
        self.is_production = False

    def __save_to_file(self, path: str):
        with open(path, "w") as f:
            json.dump(
                {
                    "db": self.db.to_save(),
                    "bcrypt_salt": base64.b64encode(self.bcrypt_salt).decode("utf-8"),
                    "jwt": self.jwt.to_save(),
                    "mail_send_api": self.mail_send_api,
                    "mail_send_token": self.mail_send_token,
                    "frontend_url": self.frontend_url,
                    "is_production": self.is_production,
                },
                f,
            )

    def bcrypt_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), self.bcrypt_salt).decode("utf-8")
