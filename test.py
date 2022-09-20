import os
import sys
from MTMS.Models import  Base
# os.system("alembic init db_repository")
from flask_sqlalchemy import SQLAlchemy
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
target_metadata = Base.metadata
# os.system('alembic revision --autogenerate')
os.system('alembic upgrade head')
# for i in target_metadata.tables:
#     print(i)
#     print(target_metadata.tables[i].columns.keys())
