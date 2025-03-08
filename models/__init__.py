from extensions import db

# Import models inside the app context to avoid circular imports
from models.user import User
from models.resume import Resume

# Explicitly define available imports
__all__ = ["User", "Resume"]
