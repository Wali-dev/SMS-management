from config import app, db_SQL
from models import SmsStats  

def init_db():
    with app.app_context():
        # Drop all tables
        db_SQL.drop_all()
        
        # Create all tables
        db_SQL.create_all()
        
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()