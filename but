from fastapi import FastAPI, Depends, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Твои данные из Supabase
URL = "https://vdmksxsiigqqfpwmuzct.supabase.co/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkbWtzeHNpaWdxcWZwd211emN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2ODk2NDUsImV4cCI6MjA5NDI2NTY0NX0.JO5p1oHZFysvICqH_kyZRvRR3-_A4T8thF1-rTa2Fr4"
supabase: Client = create_client(URL, KEY)

# Модель для регистрации (в точности как в твоем ApiService.java)
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

# Эндпоинт регистрации
@app.post("/auth/register")
async def register(body: RegisterRequest):
    # Логика работы с Supabase
    response = supabase.table("users").insert({
        "name": body.name, 
        "email": body.email, 
        "password": body.password # В идеале хешировать!
    }).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Ошибка регистрации")
    
    return {"message": "Успешно", "userId": response.data[0]['id'], "email": body.email}

# Эндпоинт получения глав
@app.get("/course/chapters")
async def get_chapters():
    response = supabase.table("chapters").select("*").execute()
    return response.data
