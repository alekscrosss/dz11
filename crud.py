from security import get_password_hash
from sqlalchemy.orm import Session
import models
import schemas
from datetime import date, timedelta

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()
def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    new_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def get_user_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int):
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        for key, value in contact.dict(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_upcoming_birthdays(db: Session, user_id: int, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        models.Contact.birthday >= today,
        models.Contact.birthday <= end_date
    ).all()
