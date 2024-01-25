from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    cell_num: str
    hobby: str


class Employee(BaseModel):
    username: str
    email: str
    cell_num: str
    job: str


class All(BaseModel):
    username: str

    class Config:
        orm_mode = True
