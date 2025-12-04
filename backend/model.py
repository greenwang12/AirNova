from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy import JSON as SAJSON


# Enums
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


# Company
class Company(SQLModel, table=True):
    __tablename__ = "company"

    Company_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: str
    Type: str
    History: Optional[str] = None

    flights: List["Flight"] = Relationship(back_populates="company")
    payments: List["Payment"] = Relationship(back_populates="company")


# Customer
class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    Customer_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: str
    Email: str
    Phone: str
    Password: str
    Role: UserRole = Field(default=UserRole.CUSTOMER)

    bookings: List["Booking"] = Relationship(back_populates="customer")
    payments: List["Payment"] = Relationship(back_populates="customer")


# Flight
class Flight(SQLModel, table=True):
    __tablename__ = "flight"

    Flight_ID: Optional[int] = Field(default=None, primary_key=True)
    Company_ID: int = Field(foreign_key="company.Company_ID")

    Dept_Location: str
    Arr_Location: str
    Departure_Time: datetime
    Arrival_Time: datetime
    Seats: int

    # NEW: price per seat in rupees (float)
    Price_Per_Seat: float = Field(default=1000.0)

    Status: FlightStatus = Field(default=FlightStatus.ON_TIME)

    company: Optional[Company] = Relationship(back_populates="flights")
    bookings: List["Booking"] = Relationship(back_populates="flight")


# Booking
class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    Booking_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Flight_ID: int = Field(foreign_key="flight.Flight_ID")

    Seats: int = Field(default=1)
    Status: BookingStatus = Field(default=BookingStatus.CONFIRMED)

    Razorpay_Order_ID: Optional[str] = None
    Razorpay_Payment_ID: Optional[str] = None

    Created_At: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional[Customer] = Relationship(back_populates="bookings")
    flight: Optional[Flight] = Relationship(back_populates="bookings")


# Payment
class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    Payment_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Company_ID: Optional[int] = Field(default=None, foreign_key="company.Company_ID")

    Amount: float
    Tax: float
    Payment_Date: datetime = Field(default_factory=datetime.utcnow)
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


# PriceAlert / Notification / GroupBooking
class PriceAlert(SQLModel, table=True):
    __tablename__ = "price_alert"

    PriceAlert_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Route: str
    Target_Price: float
    Active: bool = Field(default=True)
    Created_At: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[Dict] = Field(default=None, sa_column=Column(SAJSON, nullable=True))


class Notification(SQLModel, table=True):
    __tablename__ = "notification"

    Notification_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Kind: str
    Payload: Optional[Dict] = Field(default=None, sa_column=Column(SAJSON, nullable=True))
    Sent: bool = Field(default=False)
    Created_At: datetime = Field(default_factory=datetime.utcnow)


class GroupBooking(SQLModel, table=True):
    __tablename__ = "group_booking"

    Group_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: Optional[str] = None
    Owner_Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Members: Optional[List] = Field(default=None, sa_column=Column(SAJSON, nullable=True))
    Created_At: datetime = Field(default_factory=datetime.utcnow)
