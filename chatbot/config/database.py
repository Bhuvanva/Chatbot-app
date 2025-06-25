import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        print("Database connected")
    except SQLAlchemyError as e:
        print(f"Database connection failed: {e}")

async def show_tables():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print("Tables in database:")
            for table in tables:
                print(f"- {table}")
            return tables
    except SQLAlchemyError as e:
        print(f"Failed to fetch tables: {e}")
        return [] 