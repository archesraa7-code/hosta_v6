
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey,
    func, Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, future=True, echo=False)
else:
    DB_PATH = os.environ.get("HOTEL_DB_PATH", os.path.join(os.path.dirname(__file__), "hotel.db"))
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True, echo=False)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # demo only
    role = Column(String, default="admin")
    created_at = Column(DateTime, default=func.now())

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    bookings = relationship("Booking", back_populates="hotel")

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    notes = Column(Text, nullable=True)
    tiers = relationship("MealTier", back_populates="restaurant", cascade="all, delete-orphan")

class MealTier(Base):
    __tablename__ = "meal_tiers"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String, nullable=False)  # Adult / Child / Infant ... (or عربي)
    daily_price = Column(Float, default=0.0)  # price for full day (3 meals) per person
    restaurant = relationship("Restaurant", back_populates="tiers")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company = Column(String, nullable=True)   # optional company
    agent = Column(String, nullable=True)     # المندوب
    created_at = Column(DateTime, default=func.now())
    bookings = relationship("Booking", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    booking_no = Column(String, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)

    check_in = Column(Date, nullable=True)
    check_out = Column(Date, nullable=True)
    nights = Column(Integer, default=0)

    rooms = Column(Integer, default=1)
    room_price = Column(Float, default=0.0)
    rooms_total = Column(Float, default=0.0)
    rooms_numbers = Column(String, nullable=True)  # "811-816-822"

    meals_json = Column(Text, nullable=True)
    meals_total = Column(Float, default=0.0)

    total = Column(Float, default=0.0)
    paid = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    hotel = relationship("Hotel", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    restaurant = relationship("Restaurant")

class Voucher(Base):
    __tablename__ = "vouchers"
    id = Column(Integer, primary_key=True)
    vtype = Column(String, nullable=False)  # 'receipt' or 'payment'
    number = Column(String, nullable=False, index=True)  # numeric-only
    date = Column(Date, default=func.current_date())
    amount = Column(Float, default=0.0)
    party = Column(String, nullable=False)  # from/to
    method = Column(String, default="cash")  # fixed 'cash'
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    notes = Column(Text, nullable=True)

def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    defaults = {
        "LANG": "AR",
        "COMPANY_NAME": "شركة هيلبن لخدمات المعتمرين",
        "COMPANY_VAT_ID": "",
        "COMPANY_PHONE": "",
        "COMPANY_ADDRESS": "",
        "NEXT_INVOICE_NO": "1",
        "NEXT_RCPT_NO": "1",
        "NEXT_PAY_NO": "1",
        "DEFAULT_USD_RATE": "3.7"
    }
    for k, v in defaults.items():
        if not session.query(Setting).filter_by(key=k).first():
            session.add(Setting(key=k, value=v))

    if not session.query(User).filter_by(username="admin").first():
        session.add(User(username="admin", password="1234", role="admin"))

    for rname in ["أطلس", "فاروق"]:
        if not session.query(Restaurant).filter_by(name=rname).first():
            session.add(Restaurant(name=rname))

    session.commit()
    return session
