from sqlalchemy import create_engine
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin, ModelView

from models import User, Employee, All

engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})

app = Starlette() # FastAPI()

admin = Admin(engine)

admin.add_view(ModelView(User))
admin.add_view(ModelView(Employee))
admin.add_view(ModelView(All))

admin.mount_to(app)