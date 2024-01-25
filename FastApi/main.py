import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette_admin.contrib.sqla import Admin, ModelView
from database import AsyncSessionLocal
from models import User as ModelUser, AsyncSessionLocal
from models import Employee as ModelEmployee
from models import All as ModelAll
from schema import User as SchemaUser
from schema import Employee as SchemaEmployee

# Load environment variables from .env file
load_dotenv()

# Create an SQLite engine for FastAPI app and another for Starlette Admin
app_engine = create_engine(os.environ['DATABASE_URL'])
admin_engine = create_engine(os.environ['DATABASE_URL'])

# Create a FastAPI app
app = FastAPI()

# Create a Starlette Admin instance
admin = Admin(admin_engine)
admin.add_view(ModelView(ModelUser))
admin.add_view(ModelView(ModelEmployee))
admin.add_view(ModelView(ModelAll))

# Security configuration for HTTP Basic Authentication
security = HTTPBasic()


# Dependency to authenticate users
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == "admin"
    correct_password = credentials.password == "password"
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Database Session Dependency
def get_db_url():
    return os.environ['DATABASE_URL']


# Database Session Dependency
def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post('/user/', response_model=SchemaUser)
async def create_user(user: SchemaUser, db: AsyncSession = Depends(get_db)):
    # Check if a user with the same email already exists
    existing_email = await db.execute(
        ModelUser.__table__.select().where(ModelUser.email == user.email)
    )
    existing_email = existing_email.scalar()
    if existing_email:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Check if a user with the same username already exists
    existing_username = await db.execute(
        ModelUser.__table__.select().where(ModelUser.username == user.username)
    )
    existing_username = existing_username.scalar()
    if existing_username:
        raise HTTPException(status_code=400, detail="This username is taken")

    # Create a new user
    db_user = ModelUser(
        username=user.username,
        email=user.email.lower(),
        cell_num=user.cell_num,
        hobby=user.hobby
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@app.post('/employee/', response_model=SchemaEmployee)
async def create_employee(employee: SchemaEmployee, db: AsyncSession = Depends(get_db)):
    # Check if an employee with the same email already exists
    existing_email = await db.execute(
        ModelEmployee.__table__.select().where(ModelEmployee.email == employee.email)
    )
    existing_email = existing_email.scalar()
    if existing_email:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    # Check if an employee with the same username already exists
    existing_username = await db.execute(
        ModelEmployee.__table__.select().where(ModelEmployee.username == employee.username)
    )
    existing_username = existing_username.scalar()
    if existing_username:
        raise HTTPException(status_code=400, detail="This username is taken")

    # Create a new employee
    db_employee = ModelEmployee(
        username=employee.username,
        email=employee.email.lower(),
        cell_num=employee.cell_num,
        job=employee.job
    )
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)

    return db_employee


@app.get('/users/')
async def get_users(db: AsyncSession = Depends(get_db)):
    stmt = select(ModelUser.username, ModelUser.hobby)
    result = await db.execute(stmt)
    users = result.fetchall()
    users_dict = [{"username": username, "hobby": hobby} for username, hobby in users]
    return users_dict


@app.get('/employees/')
async def get_employees(db: AsyncSession = Depends(get_db)):
    stmt = select(ModelEmployee.username, ModelEmployee.job)
    result = await db.execute(stmt)
    employee = result.fetchall()
    employee_dict = [{"username": username, "job": job} for username, job in employee]
    return employee_dict


@app.get('/all/')
async def get_all(db: AsyncSession = Depends(get_db)):
    stmt = select(ModelUser.username).union(select(ModelEmployee.username))
    result = await db.execute(stmt)
    all_users = result.fetchall()
    all_dict = [{"username": username} for username in all_users]
    return all_dict


@app.get('/users/{username}')
async def get_specific_user(username: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ModelUser.username, ModelUser.hobby).filter(ModelUser.username == username)
    result = await db.execute(stmt)
    user = result.first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = {"username": user.username, "hobby": user.hobby}
    return user_dict


admin.mount_to(app)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
