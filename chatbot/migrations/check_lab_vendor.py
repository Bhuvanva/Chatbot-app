import os
import asyncio
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def check_lab_vendor_table():
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
                # Check if lab_vendor table exists
                await cursor.execute("SHOW TABLES LIKE 'lab_vendor';")
                table_exists = await cursor.fetchone()
                
                if table_exists:
                    print("lab_vendor table exists")
                    # Show the table structure
                    await cursor.execute("DESCRIBE lab_vendor;")
                    table_structure = await cursor.fetchall()
                    print("\nTable Structure:")
                    for row in table_structure:
                        print(row)
                else:
                    print("lab_vendor table does not exist!")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'pool' in locals():
            pool.close()
            await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(check_lab_vendor_table()) 