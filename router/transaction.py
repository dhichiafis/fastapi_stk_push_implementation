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
async def payment_callback(request:Request,db:Session=Depends(connect)):
    pass


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

