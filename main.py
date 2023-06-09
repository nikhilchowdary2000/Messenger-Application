from fastapi import FastAPI
app = FastAPI()

from routes.user_routes import user
app.include_router(user)
