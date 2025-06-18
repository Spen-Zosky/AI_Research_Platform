# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- FIX: Add project root to Python's path ---
# This ensures the script can find the 'app' module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# --- END OF FIX ---


# Import your Base from your models.
# This works because we've adjusted the path above.
from app.models.project import Base

# --- SCRIPT MAIN LOGIC ---
def create_database_tables():
    """
    Connects to the database and creates all tables
    defined in the models that inherit from Base.
    """
    print("--- Starting Database Initialization ---")
    
    # Load environment variables from .env file
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    # --- DIAGNOSTIC STEP ---
    # Print the database URL to verify it's being loaded correctly
    print(f"DEBUG: Attempting connection with DATABASE_URL: {db_url}")
    # --- END DIAGNOSTIC STEP ---

    if not db_url:
        print("ERROR: DATABASE_URL not found in .env file.")
        return

    try:
        # Create an engine to connect to the database
        engine = create_engine(db_url)
        
        print("Creating all new tables...")
        # Create all tables that are defined in our models
        Base.metadata.drop_all(bind=engine) # Clears old tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ SUCCESS: Database initialized correctly.")

    except Exception as e:
        print(f"❌ FAILURE: An error occurred: {e}")

if __name__ == "__main__":
    create_database_tables()
