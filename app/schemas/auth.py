from pydantic import BaseModel, Field, EmailStr

class RegisterIn(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(..., min_length=6)

class LoginIn(BaseModel):
    login: str = Field(..., description="email or phone")
    password: str

class GoogleVerifyIn(BaseModel):
    credential: str = Field(..., min_length=10)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: int
    email: EmailStr | None
    phone: str | None
    role: str
