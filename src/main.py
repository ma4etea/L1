import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
# from src.database import *



import uvicorn
from fastapi import FastAPI
from src.api.hotels import router as hotels_router
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.booking import router as booking_router
from _cors_helper.load_test import router as load_test
from src.config import settings

app = FastAPI()
app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(load_test)




if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, workers=None)

# uvicorn main:app
# fastapi dev main.py
# python main.py
