from typing import Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float


class Invoice(BaseModel):
    invoice_number: str
    date: str = Field(description="YYYY-MM-DD")
    vendor: str
    customer: Optional[str] = None
    items: list[LineItem]
    subtotal: float
    tax: float
    total_amount: float
    currency: str


class Experience(BaseModel):
    company: str
    role: str
    period: str
    description: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: str
    period: str


class Resume(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str]
    experience: list[Experience]
    education: list[Education]


SCHEMAS = {"invoice": Invoice, "resume": Resume}