from fastapi import Depends, FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from project.databaseconn import Base, engine, get_db

app = FastAPI(title="My Crochet Tracker")


class DB_Project(Base):  # database model
    __tablename__ = "Crochet Projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    yarn_type = Column(String)


Base.metadata.create_all(bind=engine)


class Project(BaseModel):  # pydantic model for api and db
    id: int
    name: str
    yarn_type: str


projects: list[dict] = [
    {"p_id": 1, "p_name": "star blanket", "yarn_type": "weight 5"},
    {
        "p_id": 2,
        "p_name": "filet crochet flower",
        "yarn_type": "crochet thread size 20",
    },
    {"p_id": 3, "p_name": "filet crochet sampler", "yarn_type": "tenncel weight 2"},
]


@app.get("/", include_in_schema=False)
def home():
    return {"message": "You have reached the landing page"}


@app.get("/project")
def get_all(db: Session = Depends(get_db)):
    return db.query(DB_Project).all()


@app.get("/project/get/{id}")
def get_route(id: int, db: Session = Depends(get_db)):
    project = db.query(DB_Project).filter(DB_Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/add/")
def add_route(project: Project, db: Session = Depends(get_db)):

    if db.query(DB_Project).filter(DB_Project.name == project.name).first():
        raise HTTPException(status_code=404, detail="project alrady exists")
    else:
        new_project = DB_Project(**project.dict())
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project


"""@app.delete("/projects/delete/{id}")
def delete_route(id: int):
    for i, p in enumerate(
        projects
    ):  # enumerate gives the index as well as the contents in this case the dictinary sotred in i and p respectively
        if p["p_id"] == id:
            projects.pop(i)
            return projects

    raise HTTPException(status_code=404, detail="Project does not exist")"""


@app.put("/projects/update/{p_id}")
def update_route(id: int, project=Project, db: Session = Depends(get_db)):

    existing = db.query(DB_Project).filter(DB_Project.id == id).first()

    if (
        db.query(DB_Project)
        .filter(DB_Project.id != id, DB_Project.name == project.name)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Duplicate project exists")
    elif not existing:
        raise HTTPException(status_code=404, detail="Project not found")
    else:
        existing.name == project.name
        existing.yarn_type == project.yarn_type
        db.commit(existing)
        db.refresh(existing)
        return existing


@app.delete("/projects/delete/{id}")
def delete_route(id: int, project=Project, db: Session = Depends(get_db)):
    del_proj = db.query(DB_Project).filter(DB_Project.id == id).first()

    if not del_proj:
        raise HTTPException(status_code=404, detail="Project does not exist")
    db.delete(del_proj)
    db.commit()
