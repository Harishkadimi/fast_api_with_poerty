from fastapi import FastAPI,Depends
from database import SessionLocal, engine
import models,schemas
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post('/')
def index(request: schemas.Users,db: Session = Depends(get_db)):
    create_new_user = models.Users(username = request.username, password = request.password, created_at =request.created_at )
    db.add(create_new_user)
    db.commit()
    db.refresh(create_new_user)
    return create_new_user