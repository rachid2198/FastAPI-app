from fastapi import FastAPI, Depends, status, Response, HTTPException
from . import schemas,models
from .database import engine,SessionLocal
from sqlalchemy.orm import Session
from typing import List

app=FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(engine)

@app.get('/',status_code=status.HTTP_200_OK)
def home():
    return {"message":"hello world"}

@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(blog:schemas.Blog,db: Session=Depends(get_db)):
    new_blog= models.Blog(title=blog.title,body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return {'data':new_blog}


@app.delete('/blog/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete(id,db:Session=Depends(get_db)):
    blog=db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="blog does not exist")
    db.delete(blog)
    db.commit()
    return {'detail':'blog was deleted'}

@app.put('/blog/{id}',status_code=status.HTTP_202_ACCEPTED)
def update(id,request:schemas.Blog, db:Session=Depends(get_db)):
    blog=db.query(models.Blog).get(id)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="blog does not exist")
    db.query(models.Blog).filter(models.Blog.id==id).update(request.dict(),synchronize_session=False)
    db.commit()
    db.refresh(blog)
    return {'detail':blog}

@app.get('/blog',status_code=200,response_model=List[schemas.ShowBlog])
def all(db:Session=Depends(get_db)):
    blogs=db.query(models.Blog).all()
    return blogs

@app.get('/blog/{id}',status_code=200,response_model=schemas.ShowBlog)
def show(id, db:Session=Depends(get_db)):
    blog=db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"blog with id {id} is unavailable")
    return blog



