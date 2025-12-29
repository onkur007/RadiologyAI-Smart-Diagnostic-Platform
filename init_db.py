"""
Database initialization script.
Creates database tables and seeds initial admin user.
"""
import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models import User, UserRole
from app.utils import get_password_hash


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def create_admin_user():
    """Create initial admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if admin_exists:
            print("\n⚠️  Admin user already exists!")
            create_new = input("Create another admin? (y/n): ").lower()
            if create_new != 'y':
                return
        
        print("\n--- Create Admin User ---")
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        full_name = input("Enter admin full name: ")
        password = getpass("Enter admin password: ")
        confirm_password = getpass("Confirm password: ")
        
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return
        
        # Check if username exists
        if db.query(User).filter(User.username == username).first():
            print("❌ Username already exists!")
            return
        
        # Check if email exists
        if db.query(User).filter(User.email == email).first():
            print("❌ Email already exists!")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print("\n✅ Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_users():
    """Create sample patient and doctor users for testing"""
    db = SessionLocal()
    
    try:
        print("\n--- Creating Sample Users ---")
        
        # Sample Patient
        if not db.query(User).filter(User.username == "patient_demo").first():
            patient = User(
                username="patient_demo",
                email="patient@example.com",
                full_name="John Doe",
                hashed_password=get_password_hash("password123"),
                role=UserRole.PATIENT,
                is_active=True
            )
            db.add(patient)
            print("✅ Sample patient created (username: patient_demo, password: password123)")
        
        # Sample Doctor
        if not db.query(User).filter(User.username == "doctor_demo").first():
            doctor = User(
                username="doctor_demo",
                email="doctor@example.com",
                full_name="Dr. Jane Smith",
                hashed_password=get_password_hash("password123"),
                role=UserRole.DOCTOR,
                is_active=True
            )
            db.add(doctor)
            print("✅ Sample doctor created (username: doctor_demo, password: password123)")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("=" * 60)
    print("AI-Powered Radiology Assistant - Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create admin user
    create_admin = input("\nCreate admin user? (y/n): ").lower()
    if create_admin == 'y':
        create_admin_user()
    
    # Create sample users
    create_samples = input("\nCreate sample users for testing? (y/n): ").lower()
    if create_samples == 'y':
        create_sample_users()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("1. Configure your .env file with database and API credentials")
    print("2. Run the application: uvicorn app.main:app --reload")
    print("3. Access API documentation: http://localhost:8000/docs")
    print("\n")


if __name__ == "__main__":
    main()
