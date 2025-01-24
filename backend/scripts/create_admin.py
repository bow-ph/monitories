from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.core.auth import get_password_hash
from app.core.config import settings

# Create database if it doesn't exist
postgres_engine = create_engine(f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/postgres")
try:
    with postgres_engine.connect() as conn:
        conn.execute(text("commit"))
        conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
except Exception:
    pass
finally:
    postgres_engine.dispose()

# Create engine and session for our application database
engine = create_engine(settings.get_database_url)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Create admin user if not exists
admin_user = db.query(User).filter(User.email == 'admin@pmtool.test').first()
if not admin_user:
    admin_user = User(
        email='admin@pmtool.test',
        hashed_password=get_password_hash('admin123'),
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    print('Admin user created')
else:
    print('Admin user already exists')
