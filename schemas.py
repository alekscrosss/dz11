# файл schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str


class UserInDB(UserCreate):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None

class UserAvatarUpdate(BaseModel):
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")