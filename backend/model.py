from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy import JSON as SAJSON


# =========================
# ENUMS
# =========================
class FlightStatus(str, Enum):
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REBOOKED = "REBOOKED"
    REFUNDED = "REFUNDED"


# =========================
# COMPANY
# =========================
class Company(SQLModel, table=True):
    __tablename__ = "company"

    Company_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: str
    Type: str
    History: Optional[str] = None
    Logo_URL: Optional[str] = None

    flights: List["Flight"] = Relationship(back_populates="company")
    payments: List["Payment"] = Relationship(back_populates="company")


# =========================
# CUSTOMER
# =========================
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


# =========================
# FLIGHT  ✅ FIXED
# =========================
class Flight(SQLModel, table=True):
    __tablename__ = "flight"

    Flight_ID: Optional[int] = Field(default=None, primary_key=True)
    Company_ID: int = Field(foreign_key="company.Company_ID")

    Flight_Code: Optional[str] = None
    Dept_Location: str
    Arr_Location: str

    Departure_Time: datetime
    Arrival_Time: datetime

    Total_Seats: int
    Available_Seats: int

    Price_Per_Seat: float = 1000.0
    Stops: int = 0
    Status: FlightStatus = Field(default=FlightStatus.ON_TIME)

    # ✅ NEW FIELDS (PROPERLY INSIDE CLASS)
    Cabin_Baggage_Kg: int = Field(default=7)
    Checkin_Baggage_Kg: int = Field(default=15)

    Seat_Pricing: Dict = Field(
        default_factory=lambda: {
            "high": 800,
            "low": 300,
            "free": 0
        },
        sa_column=Column(SAJSON)
    )

    company: Optional["Company"] = Relationship(back_populates="flights")
    bookings: List["Booking"] = Relationship(back_populates="flight")


# =========================
# BOOKING
# =========================
class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    Booking_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Flight_ID: int = Field(foreign_key="flight.Flight_ID")

    Seats: int = 1
    Status: BookingStatus = Field(default=BookingStatus.CREATED)

    Razorpay_Order_ID: Optional[str] = None
    Razorpay_Payment_ID: Optional[str] = None

    Created_At: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(back_populates="bookings")
    flight: Optional["Flight"] = Relationship(back_populates="bookings")
    travellers: List["Traveller"] = Relationship(back_populates="booking")


# =========================
# PAYMENT
# =========================
class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    Payment_ID: Optional[int] = Field(default=None, primary_key=True)

    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Booking_ID: int = Field(foreign_key="booking.Booking_ID")
    Company_ID: Optional[int] = Field(default=None, foreign_key="company.Company_ID")

    Amount: float
    Tax: float = 0.0

    Gateway_Provider: str = "razorpay"
    Gateway_Txn_ID: Optional[str] = None
    Gateway_Payment_ID: Optional[str] = None

    Status: str = "created"
    Created_At: datetime = Field(default_factory=datetime.utcnow)
    Captured_At: Optional[datetime] = None

    customer: Optional["Customer"] = Relationship(back_populates="payments")
    company: Optional["Company"] = Relationship(back_populates="payments")


# =========================
# TRAVELLER
# =========================
class Traveller(SQLModel, table=True):
    __tablename__ = "traveller"

    Traveller_ID: Optional[int] = Field(default=None, primary_key=True)
    Booking_ID: int = Field(foreign_key="booking.Booking_ID")

    Full_Name: str
    Age: int
    Gender: str

    booking: Optional["Booking"] = Relationship(back_populates="travellers")


# =========================
# GROUP BOOKING
# =========================
class GroupBooking(SQLModel, table=True):
    __tablename__ = "group_booking"

    Group_ID: Optional[int] = Field(default=None, primary_key=True)
    Name: Optional[str] = None
    Owner_Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Members: Optional[List] = Field(default=None, sa_column=Column(SAJSON))
    Created_At: datetime = Field(default_factory=datetime.utcnow)


# =========================
# PRICE ALERT
# =========================
class PriceAlert(SQLModel, table=True):
    __tablename__ = "price_alert"

    PriceAlert_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Route: str
    Target_Price: float
    Active: bool = True
    Created_At: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[Dict] = Field(default=None, sa_column=Column(SAJSON))


# =========================
# NOTIFICATION
# =========================
class Notification(SQLModel, table=True):
    __tablename__ = "notification"

    Notification_ID: Optional[int] = Field(default=None, primary_key=True)
    Customer_ID: int = Field(foreign_key="customer.Customer_ID")
    Kind: str
    Payload: Optional[Dict] = Field(default=None, sa_column=Column(SAJSON))
    Sent: bool = False
    Created_At: datetime = Field(default_factory=datetime.utcnow)
