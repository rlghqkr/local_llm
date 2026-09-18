from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
import uvicorn

# 실행: uvicorn main:app --reload
# 접속: http://localhost:8000/  (또는 http://127.0.0.1:8000/)
# 문서: http://localhost:8000/docs

app = FastAPI()


# ──────────────────────────────────────────────
# DTO (데이터 전송 객체)
# ──────────────────────────────────────────────
class UserCreate(BaseModel):
    """요청 바디: 사용자 생성 시 받는 데이터"""
    username: str
    password: str
    avatar_url: HttpUrl | None = None
    user_fullname: str | None = None
    email: str | None = None

# DTO : 응답 전송 객체
class UserResponse(BaseModel):
    """응답 바디: password를 제외하고 반환"""
    username: str
    avatar_url: HttpUrl | None = None
    user_fullname: str | None = None
    email: str | None = None



# ──────────────────────────────────────────────
# GET
# ──────────────────────────────────────────────
# GET http://localhost:8000/
@app.get("/")
async def root():
    data = "DB에서 데이터 읽어오기"  # 비즈니스 로직 자리
    return {"message": data}


# GET http://localhost:8000/items
@app.get("/items")
def read_items():
    return {"item_id": 1, "q": "사과"}


# GET http://localhost:8000/items/100?q=사과
# GET http://localhost:8000/items/200?q=치킨
# GET http://localhost:8000/items/300?q=몽쉘
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    # item_id: 경로 매개변수 (int로 자동 변환·검증)
    # q: 쿼리 매개변수 (선택)
    print(f"item_id: {item_id}, q: {q}")
    return {"item_id": item_id, "q": q}


# ──────────────────────────────────────────────
# POST
# ──────────────────────────────────────────────
# POST http://localhost:8000/userid_info/
# Body(JSON): {"username": "kiho", "password": "1234"}
@app.post("/userid_info/", response_model=UserResponse)
def create_user(user: UserCreate):
    print(f"username: {user.username}")
    print(f"avatar_url: {user.avatar_url}")
    print(f"user_fullname: {user.user_fullname}")

    user_info = UserResponse(
        name=user.username,
        avatar_url=user.avatar_url,
    )
    return user_info  # response_model에 따라 password는 응답에서 제외됨


# POST http://localhost:8000/userid/1234?q=test
@app.post("/userid/{user_id}")
def create_user_by_id(user_id: int, q: str | None = None):
    print(f"user_id: {user_id}, q: {q}")
    return {"user_id": user_id, "q": q}

if __name__ == "__main__":
    
    #uvicorn.run("현재_파일이름:FastAPI객체_식별자", reload=True)
    uvicorn.run("main:app", reload=True)