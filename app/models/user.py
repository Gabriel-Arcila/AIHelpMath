from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    full_name: Optional[str] = None


class TipUser():
    def __init__(self,id:int, name:str,users:list[User] = []):
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
    def name(self, name_new:str):
        if name_new is not None and isinstance(name_new, str) and len(name_new) > 0:
            self.__name = name_new
            return "Saved"
        else:
            return "Error"

    @property
    def users(self):
        return self.__users
