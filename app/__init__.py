from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db      = SQLAlchemy()
migrate = Migrate()
login   = LoginManager()
mail    = Mail()

login.login_view          = 'auth.login'
login.login_message       = 'Please login to access this page.'
login.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app import models

    from app.routes.auth      import auth
    from app.routes.dashboard import dashboard
    from app.routes.customers import customers
    from app.routes.bikes     import bikes
    from app.routes.services  import services
    from app.routes.inventory import inventory
    from app.routes.billing   import billing

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(customers)
    app.register_blueprint(bikes)
    app.register_blueprint(services)
    app.register_blueprint(inventory)
    app.register_blueprint(billing)

    return app


# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
# from config import Config


# db       = SQLAlchemy()
# migrate  = Migrate()
# login    = LoginManager()
# login.login_view = 'auth.login'
# from app import models

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)
#     migrate.init_app(app, db)
#     login.init_app(app)

#     with app.app_context():
#         from app import models 

#     from app.routes.auth      import auth
#     from app.routes.dashboard import dashboard
#     from app.routes.customers import customers
#     from app.routes.bikes     import bikes
#     from app.routes.services  import services
#     from app.routes.inventory import inventory
#     from app.routes.billing   import billing

#     app.register_blueprint(auth)
#     app.register_blueprint(dashboard)
#     app.register_blueprint(customers)
#     app.register_blueprint(bikes)
#     app.register_blueprint(services)
#     app.register_blueprint(inventory)
#     app.register_blueprint(billing)

#     return app