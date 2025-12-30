from fastapi import APIRouter,Depends,status,Request
from sqlalchemy.orm import Session 
from model import *
from schemas import *
from database import *
from payment import *


transaction_router=APIRouter(
    prefix='/transactions',
    tags=['transactions'])


@transaction_router.post('/new',
                        response_model=TransactionBase)
async def create_transaction(
    trans:TransactionCreate,
    db:Session=Depends(connect)
):
    transaction=Transaction(
        amount=trans.amount,
        description=trans.description,
        
    )
    stk_response=get_stk_push(
        phone_number='254721676091',
        amount=trans.amount)
    transaction.type="deposit"
    transaction.status = 'pending'
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    print(stk_response)
    checkout_id = stk_response.get("CheckoutRequestID")
    if checkout_id:
        transaction.checkout_id = checkout_id
        db.commit()
    else:
        transaction.status = "failed"
        db.commit()
        print("STK push failed:", stk_response)
    return transaction


@transaction_router.post('/disburse',response_model=TransactionBase)
async def disburse_money(
    trans:TransactionCreate,
    db:Session=Depends(connect)
):
    new_transaction=Transaction(amount=trans.amount,description=trans.description)
    response=disburse_payments("254721676091",10)
    checkout_id=response.get("ConversationID")
    new_transaction.type="withdrawal"
    new_transaction.status="pending"
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    if checkout_id:
        new_transaction.checkout_id=checkout_id
        db.commit()
    else:
        new_transaction.status="failed"
        db.commit()
        print('disbursal failed',response)
    return new_transaction
@transaction_router.get('/all',response_model=List[TransactionBase])
async def get_all_transactions(
    db:Session=Depends(connect)
):
    return db.query(Transaction).all()


@transaction_router.get('/{id}',response_model=TransactionBase)
async def get_transaction(id:int,db:Session=Depends(connect)):
    transaction=db.query(Transaction).filter(Transaction.id==id).first()
    return transaction
#@transaction_router.post()
async def is_transaction_successful(
    mpesa_reciept:str,
    db:Session=Depends(connect)
):
    
    transaction=db.query(Transaction).filter(Transaction.mpesa_reciept==mpesa_reciept).first()


#its the callback that modifies the balance status of the wallet if so
@transaction_router.post('/payment/callback')
async def process_payment_callback(request:Request,db:Session=Depends(connect)):
    payload=await request.json()
    payment_callback=payload.get("Result")

    print(payment_callback)
    if not payment_callback:
        return {}
    checkout_id=payment_callback.get("ConversationID")
    transaction_id=payment_callback.get('TransactionID')
    result_code=payment_callback.get('ResultCode')
    #find the transaction wit the checkout id
    transaction=db.query(Transaction).filter(Transaction.checkout_id==checkout_id).first()
    if result_code==0:
        transaction.status="successful"
        transaction.receipt=transaction_id
    else:
        transaction.status="failed"
    db.commit()

@transaction_router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(connect)):
    """
    Handles M-Pesa STK Push callback.
    Updates transaction status based on ResultCode.
    """
    payload = await request.json()
    print("MPESA CALLBACK RECEIVED:")
    print(payload)


    # Extract the stkCallback safely
    stk_callback = payload.get("Body", {}).get("stkCallback")
    if not stk_callback:
        return {"ResultCode": 1, "ResultDesc": "Invalid payload"}

    checkout_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc", "")

    # Find the transaction by checkout_id
    transaction = db.query(Transaction).filter(Transaction.checkout_id == checkout_id).first()

    if not transaction:
        return {"ResultCode": 1, "ResultDesc": "Transaction not found"}

    # Handle successful payment
    if result_code == 0:
        callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        receipt = None
        for item in callback_metadata:
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = item.get("Value")
                break
        transaction.status = "success"
        transaction.mpesa_receipt = receipt
    else:
        # Payment failed or cancelled
        transaction.status = "failed"

    db.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}

