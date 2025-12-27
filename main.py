from fastapi import FastAPI
from router.transaction import *
import uvicorn 
from fastapi.middleware.cors import CORSMiddleware

from database import *

Base.metadata.create_all(bind=engine)
app=FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'],
                   allow_origins=['*'])
app.include_router(transaction_router)



@app.get('/')
async def home():
    return {'message':'welcome to payment intergration'}