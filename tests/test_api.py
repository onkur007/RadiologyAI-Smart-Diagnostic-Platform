"""
Unit tests for the Radiology AI application.
Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole
from app.utils import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_patient(setup_database):
    """Create a test patient user"""
    db = TestingSessionLocal()
    user = User(
        username="test_patient",
        email="patient@test.com",
        full_name="Test Patient",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.PATIENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_doctor(setup_database):
    """Create a test doctor user"""
    db = TestingSessionLocal()
    user = User(
        username="test_doctor",
        email="doctor@test.com",
        full_name="Test Doctor",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.DOCTOR
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_patient():
    """Test patient registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "newpatient",
            "email": "newpatient@test.com",
            "full_name": "New Patient",
            "password": "password123",
            "role": "patient"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newpatient"


def test_register_duplicate_username():
    """Test registration with duplicate username"""
    # First registration
    client.post(
        "/auth/register",
        json={
            "username": "duplicate",
            "email": "user1@test.com",
            "full_name": "User One",
            "password": "password123",
            "role": "patient"
        }
    )
    
    # Second registration with same username
    response = client.post(
        "/auth/register",
        json={
            "username": "duplicate",
            "email": "user2@test.com",
            "full_name": "User Two",
            "password": "password123",
            "role": "patient"
        }
    )
    assert response.status_code == 400


def test_login_success(test_patient):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_patient",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(test_patient):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        data={
            "username": "test_patient",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    response = client.get("/patients/me")
    assert response.status_code == 401


def test_get_patient_profile(test_patient):
    """Test getting patient profile"""
    # Login first
    login_response = client.post(
        "/auth/login",
        data={
            "username": "test_patient",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    response = client.get(
        "/patients/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_patient"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
