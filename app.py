from fastapi import FastAPI
from application.routes.auth_route import auth_router
from application.routes.user_route import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)

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
