from fastapi.testclient import TestClient
import pytest
from blog import models
from blog.schemas import Blog, ShowBlog
from blog.main import app, get_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

# testing database----------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog_test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db]=override_get_db
models.Base.metadata.drop_all(bind=engine)

# testing ------------------------------------------------------
@pytest.fixture
def client():
    models.Base.metadata.create_all(bind=engine)
    yield TestClient(app)


def test_root(client):
    res=client.get("/")
    assert res.json().get("message")=="hello world"
    assert res.status_code == 200


@pytest.mark.parametrize("blog",[
    ({"title":"blog 1","body":"blog text"}),
    ({"title":"blog 2","body":"blog text"}),
    ({"title":"blog 3","body":"blog text"}),
    ({"title":"blog 4","body":"blog text"}),
])
def test_create_blog(client,blog):
    res= client.post("/blog",json=blog)

    new_blog=Blog(**res.json().get("data"))
    assert res.status_code ==201


@pytest.mark.parametrize("blog_id",[
    (1),(2),(3),(4)
])
def test_get_blog(client,blog_id):
    res=client.get(f"/blog/{blog_id}")
    blog=Blog(**res.json())
    assert res.status_code==200

@pytest.mark.parametrize("blog_id, updated_blog",[
    (1,{"title":"updated blog 1","body":"updated blog text"}),
    (2,{"title":"updated blog 2","body":"updated blog text"}),
    (3,{"title":"updated blog 3","body":"updated blog text"}),
    (4,{"title":"updated blog 4","body":"updated blog text"}),
])
def test_update_blog(client,blog_id,updated_blog):
    res=client.put(f"/blog/{blog_id}",json=updated_blog)
    blog=Blog(**res.json().get("detail"))
    assert res.status_code==202
    assert blog.title==f"updated blog {blog_id}"
    assert blog.body=="updated blog text"

def test_get_blogs(client):
    res=client.get("/blog")
    assert res.status_code==200
    assert len(res.json())==4

@pytest.mark.parametrize("blog_id",[(1),(2),(3),(4)] )
def test_delete_blogs(client,blog_id):
    res=client.delete(f"/blog/{blog_id}")
    assert res.status_code==204
