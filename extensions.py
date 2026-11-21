"""
extensions.py
-------------
The database and CSRF objects are created here (without being attached to an
app) so that models.py and the route modules can import them safely without
creating circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# ORM instance used for all database models.
db = SQLAlchemy()

# Protects every POST form against Cross Site Request Forgery attacks.
csrf = CSRFProtect()
