import os
from sqlalchemy import text
import asyncio
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def create_lab_type_table():
    # Get database credentials from environment variables
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "labbuddy_database")
    
    try:
        # Create connection pool
        pool = await aiomysql.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            autocommit=True
        )
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Create the lab_type table
                create_table_query = """
                CREATE TABLE IF NOT EXISTS lab_type (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    lab_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (lab_id) REFERENCES lab_vendor(id) ON DELETE CASCADE
                );
                """
                
                await cursor.execute(create_table_query)
                print("lab_type table created successfully!")
                
                # Show the table structure
                await cursor.execute("DESCRIBE lab_type;")
                table_structure = await cursor.fetchall()
                print("\nTable Structure:")
                for row in table_structure:
                    print(row)
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'pool' in locals():
            pool.close()
            await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(create_lab_type_table()) 