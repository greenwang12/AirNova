# backend/model.py
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, List
from datetime import datetime
from enum import Enum
from typing import Dict

# =========================================================
# ENUMS
# =========================================================
class FlightStatus(str, Enum):
    ON_TIME = "On-Time"
    DELAYED = "Delayed"
    CANCELLED = "Cancelled"

class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REBOOKED = "REBOOKED"
    REFUNDED = "REFUNDED"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

# =========================================================
# COMPANY MODEL
# =========================================================
class Company(SQLModel, table=True):
    Company_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: str
    Type: str
    History: Optional[str] = None

    flights: List["Flight"] = Relationship(back_populates="company")
    payments: List["Payment"] = Relationship(back_populates="company")

# =========================================================
# CUSTOMER MODEL
# =========================================================
class Customer(SQLModel, table=True):
    Customer_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: str
    Email: str
    Phone: str
    Password: str
    Role: UserRole = Field(default=UserRole.CUSTOMER)

    bookings: List["Booking"] = Relationship(back_populates="customer")
    payments: List["Payment"] = Relationship(back_populates="customer")

# =========================================================
# FLIGHT MODEL
# =========================================================
class Flight(SQLModel, table=True):
    Flight_ID: Optional[int] = Field(default=None, primary_key=True)
    Company_ID: int = Field(foreign_key="company.Company_ID")

    Dept_Location: str
    Arr_Location: str
    Departure_Time: datetime
    Arrival_Time: datetime
    Seats: int

    Status: FlightStatus = Field(default=FlightStatus.ON_TIME)

    company: Optional[Company] = Relationship(back_populates="flights")
    bookings: List["Booking"] = Relationship(back_populates="flight")

# =========================================================
# BOOKING MODEL
# =========================================================
class Booking(SQLModel, table=True):
    Booking_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Flight_ID: int = Field(foreign_key="flight.Flight_ID")

    Seats: int = 1
    Status: BookingStatus = Field(default=BookingStatus.CONFIRMED)

    Razorpay_Order_ID: Optional[str] = None
    Razorpay_Payment_ID: Optional[str] = None

    Created_At: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional[Customer] = Relationship(back_populates="bookings")
    flight: Optional[Flight] = Relationship(back_populates="bookings")

# =========================================================
# PAYMENT MODEL
# =========================================================
class Payment(SQLModel, table=True):
    Payment_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Company_ID: Optional[int] = Field(default=None, foreign_key="company.Company_ID")

    Amount: float
    Tax: float
    Payment_Date: datetime
    Payment_Type: str

    Card_Last4: Optional[str] = None
    Card_Brand: Optional[str] = None
    Gateway_Provider: Optional[str] = None
    Gateway_Txn_ID: Optional[str] = None
    Captured_At: Optional[datetime] = None
    Status: str = Field(default="created")
    Idempotency_Key: Optional[str] = None

    customer: Optional[Customer] = Relationship(back_populates="payments")
    company: Optional[Company] = Relationship(back_populates="payments")


# --- fixed models (replace your earlier PriceAlert/Notification/GroupBooking) ---
class PriceAlert(SQLModel, table=True):
    PriceAlert_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Route: str
    Target_Price: float
    Active: bool = Field(default=True)
    Created_At: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))

class Notification(SQLModel, table=True):
    Notification_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Kind: str
    Payload: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    Sent: bool = Field(default=False)
    Created_At: datetime = Field(default_factory=datetime.utcnow)

class GroupBooking(SQLModel, table=True):
    Group_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: Optional[str] = None
    Owner_Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Members: Optional[list] = Field(default=None, sa_column=Column(JSON, nullable=True))  # store list as JSON
    Created_At: datetime = Field(default_factory=datetime.utcnow)
