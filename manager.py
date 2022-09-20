from MTMS import create_app, db_session
from MTMS.Models.applications import *
from MTMS.Models.courses import *
from MTMS.Models.users import *
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)



manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()