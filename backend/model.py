# backend/model.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date, datetime

class Company(SQLModel, table=True):
    C_ID: Optional[int] = Field(default=None, primary_key=True)
    C_Name: str
    C_Type: str

class Flight(SQLModel, table=True):
    F_ID: Optional[int] = Field(default=None, primary_key=True)
    F_Dept_Location: str
    F_Arr_Location: str
    F_Company: str
    F_Duration: int
    F_Dept_Time: datetime
    F_Arr_Time: datetime
    F_Seats: int
    C_ID: Optional[int] = Field(default=None, foreign_key="company.C_ID")

class Customer(SQLModel, table=True):
    Cust_ID: Optional[int] = Field(default=None, primary_key=True)
    Cust_Name: str
    Cust_Gender: Optional[str] = None           # nullable in DB
    Cust_DOB: date
    Cust_State: str                              # NOT NULL in your DB
    Cust_Country: str                            # NOT NULL in your DB
    Cust_Pincode: Optional[str] = None
    Cust_Login: str
    Cust_Password: str
    PhoneNumber: Optional[str] = None
    
class Payment(SQLModel, table=True):
    Payment_ID: Optional[int] = Field(default=None, primary_key=True)
    Payment_Customer_ID: int
    Payment_Cost: float
    Payment_Tax: float
    Payment_Date: date
    Payment_Type: str
    Payment_Card_No: Optional[str] = None
    F_Company: Optional[str] = None

    # gateway fields (optional in model)
    gateway_provider: Optional[str] = None
    gateway_txn_id: Optional[str] = None
    status: Optional[str] = None
    last4: Optional[str] = None
    card_brand: Optional[str] = None
    idempotency_key: Optional[str] = None
    captured_at: Optional[datetime] = None

class Cancellation(SQLModel, table=True):
    Canc_ID: Optional[int] = Field(default=None, primary_key=True)
    Canc_Payment_ID: int
    Canc_Refund: float
    Canc_Date: date
    F_Company: Optional[str] = None
