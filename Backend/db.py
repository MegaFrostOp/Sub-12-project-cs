from sqlalchemy import create_engine , text
from sqlalchemy.orm import sessionmaker, declarative_base


DB_USER = "postgres.xupbqvkxtcyqfohbxpqa"
DB_PASSWORD = "mayoorprivateschoolsubstitution2526"
DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"


DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine & session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Base class for ORM
Base = declarative_base()

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))
        print("Database connected:", result.fetchone())
except Exception as e:
    print("DB connection error:", e)
