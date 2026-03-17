from typing import Optional

from sqlmodel import Field, SQLModel
from pydantic import BaseModel


# class User(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     email: str = Field(index=True, unique=True)
#     hashed_password: str
#     is_active: bool = Field(default=True)s
#     full_name: Optional[str] = None


class User(BaseModel):
    id: int
    email: str
    hashed_password: str
    is_active: bool
    full_name: str | None

    def __init__(
        self,
        id: int,
        email: str,
        hashed_password: str,
        is_active: bool,
        full_name: str | None,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.full_name = full_name

    def __str__(self):
        return f"User(id={self.id}, email={self.email},is_active={self.is_active}"

    @property
    def id(self):
        return self.id

    @property
    def email(self):
        return self.email

    @property
    def hashed_password(self):
        return self.hashed_password

    @property
    def is_active(self):
        return self.is_active

    @property
    def full_name(self):
        return self.full_name

    @full_name.setter
    def full_name(self, full_name_new: str):
        if (
            full_name_new is not None
            and isinstance(full_name_new, str)
            and len(full_name_new) > 0
        ):
            self.full_name = full_name_new
            return "Saved"
        else:
            return "Error"


class TipUser:
    def __init__(self, id: int, name: str, users: list[User] = []):
        self.__id = id
        self.__name = name
        self.__users = users

    def __str__(self):
        return f"TipUser(id={self.__id}, name={self.__name}, users={self.__users})"

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name_new: str):
        if name_new is not None and isinstance(name_new, str) and len(name_new) > 0:
            self.__name = name_new
            return "Saved"
        else:
            return "Error"

    @property
    def users(self):
        return self.__users
