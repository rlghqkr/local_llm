from fastapi import FastAPI, Form, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base

import models 

Base.metadata.create_all(bind=engine)

# FastAPI() 객체 생성
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

abs_path = os.path.dirname(os.path.realpath(__file__))

# templates 폴더 식별
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static/ 폴더를 fastapi에서 인식할 수 있도록 마운트시킴
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# http://localhost:8000
@app.get("/")
def home(request: Request,
         db_ss:Session = Depends(get_db)):
    todos_list = db_ss.query(models.Todo).order_by(models.Todo.id.desc()).all()
   # print(todos_list)
    for todo in todos_list:
        print(todo.id, todo.task)

    return templates.TemplateResponse(
        request = request,
        name = "index.html",
        context={ "todos": todos_list}
        )
    


# todo 데이터를 받아서 DB 테이블에 저장하기
@app.post("/add")
def add(request: Request,
        task:str=Form(...),
        db_ss:Session = Depends(get_db)):
    print(task)
    
    # task 데이터를 받고, todo 클래스 통해서, 테이블과 연결된 객체생성
    todo = models.Todo(task=task)
    # todos 테이블에 todo 객체 추가
    db_ss.add(todo)


    # 테이블에 반영
    db_ss.commit()

    # 엔드포인트 함수 home으로 redirect (POST -> GET 이므로 303)
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


# todo 수정할 레코드 조회
@app.get("/edit/{todo_id}")
def edit(request: Request, todo_id: int , db_ss: Session = Depends(get_db)):
    # 요청 수정 처리
    todo = db_ss.query(models.Todo).filter(models.Todo.id==todo_id).first()
    print(todo.task)

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return templates.TemplateResponse(
        request=request,
        name = "edit.html",
        context = {"todo": todo}
    )
  
# todo 업데이터 처리
@app.post("/edit/{todo_id}")
def update(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(False), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# todo 삭제 처리
@app.get("/delete/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    
    #uvicorn.run("현재_파일이름:FastAPI객체_식별자", reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)