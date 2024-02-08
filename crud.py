from sqlalchemy.orm import Session
import models
import schemas
from datetime import date, timedelta


def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        update_data = contact.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def get_upcoming_birthdays(db: Session, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)
    return db.query(models.Contact).filter(models.Contact.birthday >= today, models.Contact.birthday <= end_date).all()
