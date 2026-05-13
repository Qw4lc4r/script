from fastapi import FastAPI, Header, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Твои данные из Supabase
SUPABASE_URL = "https://vdmksxsiigqqfpwmuzct.supabase.co/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkbWtzeHNpaWdxcWZwd211emN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2ODk2NDUsImV4cCI6MjA5NDI2NTY0NX0.JO5p1oHZFysvICqH_kyZRvRR3-_A4T8thF1-rTa2Fr4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- МОДЕЛИ ЗАПРОСОВ ---
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- API МЕТОДЫ ---

@app.post("/auth/register")
async def register(body: RegisterRequest):
    # 1. Просто вставляем данные в таблицу (без отправки почты)
    res = supabase.table("users").insert({
        "name": body.name,
        "email": body.email,
        "password": body.password
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=400, detail="Ошибка регистрации")
    
    user = res.data[0]
    
    # 2. Возвращаем структуру LoginResponse, чтобы Android сразу авторизовал
    return {
        "message": "Success",
        "token": f"bypass_token_{user['id']}",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        }
    }

# # 1. РЕГИСТРАЦИЯ (Отправляет код на почту через Supabase Auth)
# @app.post("/auth/register")
# async def register(body: RegisterRequest):
#     try:
#         # Регистрация в системной таблице auth.users
#         auth_res = supabase.auth.sign_up({
#             "email": body.email,
#             "password": body.password,
#             "options": {
#                 "data": {"display_name": body.name}
#             }
#         })
        
#         # Дублируем данные в твою публичную таблицу users для связи с прогрессом
#         # Используем email как ключ, либо можно добавить колонку id_uuid
#         supabase.table("users").insert({
#             "name": body.name,
#             "email": body.email,
#             "password": body.password  # В продакшене лучше не хранить тут пароль в открытом виде
#         }).execute()

#         return {"message": "Код подтверждения отправлен на почту!"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # 2. ПОДТВЕРЖДЕНИЕ КОДА (OTP)
# @app.post("/auth/verify-email")
# async def verify_email(body: VerifyEmailRequest):
#     try:
#         # Проверяем цифровой код из письма
#         verify_res = supabase.auth.verify_otp({
#             "email": body.email,
#             "token": body.code,
#             "type": "signup"
#         })
        
#         # Получаем данные пользователя из нашей таблицы для Android
#         user_res = supabase.table("users").select("*").eq("email", body.email).single().execute()
        
#         return {
#             "message": "Success",
#             "token": verify_res.session.access_token,
#             "user": user_res.data
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Неверный код или срок его действия истек")

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
