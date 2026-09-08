from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AuthIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: Optional[str] = ""

class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=10, le=80)
    height: float = Field(gt=80, lt=250)
    weight: float = Field(gt=20, lt=300)

class SettingsIn(BaseModel):
    amie_name: str = Field(min_length=1, max_length=40)
    amie_avatar: str = Field(pattern="^(bear|bunny|cat)$")
    theme: str = Field(pattern="^(light|dark)$")

class ScreeningInput(BaseModel):
    age: int = Field(ge=10, le=80)
    bmi: float = Field(gt=10, lt=70)
    cycle_regular: int = Field(ge=0, le=1)
    cycle_length: float = Field(ge=15, le=90)
    missed_periods: int = Field(ge=0, le=12)
    acne: int = Field(ge=0, le=1)
    excess_hair: int = Field(ge=0, le=1)
    hair_thinning: int = Field(ge=0, le=1)
    weight_change: int = Field(ge=0, le=1)
    dark_skin: int = Field(ge=0, le=1)
    fatigue: int = Field(ge=0, le=1)
    stress: float = Field(ge=0, le=10)
    sleep: float = Field(ge=0, le=14)
    activity: float = Field(ge=0, le=20)

class CycleIn(BaseModel):
    start_date: str
    end_date: Optional[str] = ""
    flow: str = "Medium"
    cramps: int = 0
    mood: str = "Okay"
    energy: int = 3

class SymptomIn(BaseModel):
    symptom: str
    severity: int = 2
    date: str

class CheckinIn(BaseModel):
    mood: int = 3
    energy: int = 3
    stress: int = 3
    sleep: float = 7

class AmieIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
