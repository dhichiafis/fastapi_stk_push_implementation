from sqlalchemy import Column,Integer,ForeignKey,String,Float,DateTime
from datetime import datetime 
from database import *
class Transaction(Base):
    __tablename__='transactions'
    id=Column('id',Integer,primary_key=True)
    amount=Column('amount',Integer) #the daraja endpoint expects an integer datatype not float
    description=Column('description',String)
    checkout_id=Column('checkout_id',String,nullable=True)#now the transaction is asynchronous the user has not enter pin so we have to wait 
    status=Column('status',String)#pending,approved,failed ,successful
    create_at=Column('create_at',DateTime,default=datetime.now)