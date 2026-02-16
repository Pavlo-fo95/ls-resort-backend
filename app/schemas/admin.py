from pydantic import BaseModel, EmailStr, Field

class AdminBootstrapIn(BaseModel):
    secret: str = Field(..., min_length=1)
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr | None = None
    phone: str | None = None
    role: str

    model_config = {"from_attributes": True}
