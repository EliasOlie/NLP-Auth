from fastapi import FastAPI
from application.routes import user_router
from application.routes import auth_router
from application.routes import system_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(system_router.router)

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
    return {"Message" : "This is just an API, see /docs for reference and testing"}
