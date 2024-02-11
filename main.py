# файл main.py

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from models import User, get_db, engine
from schemas import UserCreate, Token, Contact
from security import create_access_token, get_current_user, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

load_dotenv()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешите все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешите все методы
    allow_headers=["*"],  # Разрешите все заголовки
)

@app.post("/users/{user_id}/avatar")
def update_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user's avatar")
    return crud.update_user_avatar(db=db, user_id=user_id, image_file=file.file)

@app.get("/verify/{verification_code}")
def verify_email(verification_code: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_code == verification_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    user.verification_code = None  # Удалите код после верификации
    db.commit()
    return {"message": "Email successfully verified"}

@app.post("/users/", response_model=schemas.UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/contacts/", response_model=schemas.Contact)
@limiter.limit("5/minute")
def create_contact(request: Request, contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    contacts = crud.get_user_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts


@app.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)


@app.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)


@app.get("/contacts/upcoming_birthdays/")
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
