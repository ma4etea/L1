import asyncio
import time
from fastapi import APIRouter


router = APIRouter(tags=["тест нагрузки"])


@router.get("/sync/{id}")
def sync_func(id: int):
    print(f"sync {id} начал: {time.time():.2f}")
    time.sleep(3)
    print(f"sync {id} закончил: {time.time():.2f}")


@router.get("/async/{id}")
async def async_func(id: int):
    print(f"async {id} начал: {time.time():.2f}")
    await asyncio.sleep(3)
    print(f"async {id} закончил: {time.time():.2f}")
