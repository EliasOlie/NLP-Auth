from fastapi import FastAPI
from application.routes import user_router
from fastapi.middleware.cors import CORSMiddleware
from application.infra.DB.DB import DB as Connection

app = FastAPI()

app.include_router(user_router.router)

#CORS Policy
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {"Hello from:" : "FastAPI backend!"}
