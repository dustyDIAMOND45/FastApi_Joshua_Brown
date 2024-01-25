import asyncio

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown_db():
    await engine.dispose()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    cell_num = Column(String)
    hobby = Column(String)
    employees = relationship("Employee", back_populates="user")
    all_entries = relationship("All", back_populates="user")

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    cell_num = Column(String)
    job = Column(String)

    # Relationship with User
    user_username = Column(String, ForeignKey("users.username"))
    user = relationship("User", back_populates="employees")

    # Relationship with All
    all_entries = relationship("All", back_populates="employee")

class All(Base):
    __tablename__ = 'all'

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="all_entries")

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="all_entries")


# Create an AsyncSession class for asynchronous database operations
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Example usage of the asynchronous code
async def create_user(user_data):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(**user_data)
            session.add(user)


async def create_employee(employee_data):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            employee = Employee(**employee_data)
            session.add(employee)


async def create_all(all_data):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            all_entry = All(**all_data)
            session.add(all_entry)


# Example of initializing and shutting down the database
async def main():
    await init_db()

    user_data = {
        "username": "example_user",
        "email": "example@example.com",
        "cell_num": "1234567890",
        "hobby": "Reading",
    }
    employee_data = {
        "username": "example_employee",
        "email": "employee@company.com",
        "cell_num": "0129345678",
        "job": "Admin",
    }
    all_data = {
        "user_id": 1,
        "employee_id": 1,
    }

    await create_user(user_data)
    await create_employee(employee_data)
    await create_all(all_data)
    # Other operations can be performed here

    await shutdown_db()


# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
