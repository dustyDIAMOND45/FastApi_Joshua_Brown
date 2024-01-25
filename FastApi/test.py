from unittest import mock
from schema import User as UserSchema
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


async def async_set_up(self):
    self.db_session = mock.AsyncMock()
    self.user_data = UserSchema(username="TestUser123", email="test@gmail.com", cell_num="0112345674", hobby="TestHobby")
    self.db_session.add = mock.MagicMock()
    
