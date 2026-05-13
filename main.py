from fastapi import FastAPI, Header, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Твои данные из Supabase
URL = "https://vdmksxsiigqqfpwmuzct.supabase.co/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkbWtzeHNpaWdxcWZwd211emN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2ODk2NDUsImV4cCI6MjA5NDI2NTY0NX0.JO5p1oHZFysvICqH_kyZRvRR3-_A4T8thF1-rTa2Fr4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- МОДЕЛИ ЗАПРОСОВ ---
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- API МЕТОДЫ ---

# 1. Регистрация
@app.post("/auth/register")
async def register(body: RegisterRequest):
    # В Supabase Auth регистрация идет отдельно, 
    # но для простоты пишем в твою таблицу users
    res = supabase.table("users").insert({
        "name": body.name,
        "email": body.email,
        "password": body.password
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=400, detail="Registration failed")
    
    user = res.data[0]
    return {"message": "Success", "userId": user['id'], "email": user['email']}

# 2. Логин
@app.post("/auth/login")
async def login(body: LoginRequest):
    res = supabase.table("users").select("*").eq("email", body.email).eq("password", body.password).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = res.data[0]
    return {
        "message": "Success",
        "token": "fake-jwt-token", # Supabase Auth выдает реальный, но пока так
        "user": {"id": user['id'], "name": user['name'], "email": user['email']}
    }

# 3. Список глав (для Chapter.java)
@app.get("/course/chapters", response_model=List[dict])
async def get_chapters():
    res = supabase.table("chapters").select("*").order("position").execute()
    return res.data

# 4. Список подглав (для Subchapter.java)
@app.get("/course/chapters/{chapterId}/subchapters")
async def get_subchapters(chapterId: int):
    res = supabase.table("subchapters").select("*").eq("chapter_id", chapterId).order("position").execute()
    return res.data

# 5. Материалы (для Material.java)
@app.get("/course/subchapters/{subchapterId}/materials")
async def get_materials(subchapterId: int):
    res = supabase.table("materials").select("*").eq("subchapter_id", subchapterId).execute()
    # Твой Android ждет объект MaterialsResponse, подстроим под него
    return {"materials": res.data}

# 6. Задачи (для Task.java)
@app.get("/tasks/subchapter/{subchapterId}")
async def get_tasks(subchapterId: int):
    # Получаем задачи и вложенные опции
    res = supabase.table("tasks").select("*, task_options(*)").eq("subchapter_id", subchapterId).execute()
    
    # Форматируем для Android (переименовываем task_options в options)
    tasks = []
    for t in res.data:
        t['options'] = t.pop('task_options')
        tasks.append(t)
    return tasks

# Тестовая проверка
@app.get("/")
def root():
    return {"message": "C# Manual API is Live!"}
