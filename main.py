from databaseconn import Base, engine, get_db
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

app = FastAPI(title="My Crochet Tracker")
template = Jinja2Templates(directory="templates")


class DB_Project(Base):  # database model
    __tablename__ = "Crochet Projects"
    id = Column(Integer, index=True, primary_key=True)
    name = Column(String, nullable=False)
    yarn_type = Column(String)


Base.metadata.create_all(bind=engine)


class Project(BaseModel):  # pydantic model for api and db
    id: int
    name: str
    yarn_type: str


@app.get("/", include_in_schema=False)
def home(request: Request):
    return template.TemplateResponse(
        "home.html", {"request": request, "message": "Hi, This is StitchMarker"}
    )


@app.get("/projects/get_form")
def get_form(request: Request):
    return template.TemplateResponse("form.html", {"request": request})


@app.post("/api/projects/add/")
def add_route(project: Project, db: Session = Depends(get_db)):

    if db.query(DB_Project).filter(DB_Project.name == project.name).first():
        raise HTTPException(status_code=404, detail="project alrady exists")
    else:
        new_project = DB_Project(**project.dict())
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project


@app.post("/projects/add/")
def post_form(
    request: Request,
    db: Session = Depends(get_db),
    p_number: int = Form(...),
    p_name: str = Form(...),
    yarn: str = Form(...),
):

    if (
        db.query(DB_Project).filter(DB_Project.name == p_name).first()
        or db.query(DB_Project).filter(DB_Project.id == p_number).first()
    ):
        return template.TemplateResponse(
            "form.html", {"request": request, "error": "Duplicate project exists"}
        )
    else:
        project = DB_Project(id=p_number, name=p_name, yarn_type=yarn)
        db.add(project)
        db.commit()
        db.refresh(project)

    return RedirectResponse(url="/projects/get", status_code=303)


@app.get("/projects/get")
def get_all(request: Request, db: Session = Depends(get_db)):
    projects = db.query(DB_Project).all()
    return template.TemplateResponse(
        "index.html", {"request": request, "projects": projects}
    )


@app.get("/api/project/get/{id}")
def get_route(request: Request, id: int, db: Session = Depends(get_db)):
    project = db.query(DB_Project).filter(DB_Project.id == id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return template.TemplateResponse(
        "get_template.html", {"request": request, "project": project}
    )


"""@app.delete("/projects/delete/{id}")
def delete_route(id: int):
    for i, p in enumerate(
        projects
    ):  # enumerate gives the index as well as the contents in this case the dictinary sorted in i and p respectively
        if p["p_id"] == id:
            projects.pop(i)
            return projects

    raise HTTPException(status_code=404, detail="Project does not exist")"""


@app.get("/projects/update/{id}")
def update(request: Request, id: int, db: Session = Depends(get_db)):
    project = db.query(DB_Project).filter(DB_Project.id == id).first()
    return template.TemplateResponse(
        "update.html", {"request": request, "project": project}
    )


@app.post("/projects/update/{id}")
def post_form(
    request: Request,
    id: int,
    p_name: str = Form(...),
    yarn: str = Form(...),
    db: Session = Depends(get_db),
):
    dupe = (
        db.query(DB_Project)
        .filter(DB_Project.id != id, DB_Project.name == p_name)
        .first()
    )
    if dupe:
        return template.TemplateResponse(
            "update.html",
            {
                "request": request,
                "project": dupe,
                "error": "Duplicate Project exists",
            },
        )

    else:

        project = db.query(DB_Project).filter(DB_Project.id == id).first()
        project.name = p_name
        project.yarn_type = yarn

        db.commit()
        return RedirectResponse(url="/projects/get", status_code=303)


@app.put("/api/projects/update/{id}")
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


@app.delete("/api/projects/delete/{id}")
def delete_route(id: int, project=Project, db: Session = Depends(get_db)):
    del_proj = db.query(DB_Project).filter(DB_Project.id == id).first()

    if not del_proj:
        raise HTTPException(status_code=404, detail="Project does not exist")
    db.delete(del_proj)
    db.commit()


@app.post("/projects/delete/{id}")
def delete_route(id: int, db: Session = Depends(get_db)):
    del_proj = db.query(DB_Project).filter(DB_Project.id == id).first()

    if not del_proj:
        raise HTTPException(status_code=404, detail="Project does not exist")
    db.delete(del_proj)
    db.commit()
    return RedirectResponse(url="/projects/get", status_code=303)
