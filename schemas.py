from pydantic import BaseModel,ConfigDict 
from datetime import datetime
from typing import Optional,List
class TransactionCreate(BaseModel):
    amount:int
    description:Optional[str]=None
    
    


class TransactionBase(TransactionCreate):
    id:int 
    status:str 
    create_at:datetime
    type:str 
    mpesa_receipt:Optional[str]=None
    checkout_id:Optional[str]=None
    model_config=ConfigDict(from_attributes=True)