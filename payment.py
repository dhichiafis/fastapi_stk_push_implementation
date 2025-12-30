import requests 
import json 
from requests.auth import HTTPBasicAuth
from datetime import timedelta,time,datetime
import base64

def get_access_token():
    #url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    #CONSUMER_KEY="kYrR8xjbpOa5XjRLuChNmcYaK8SEXzj2tyqaAV1mRc1ZtQvw"
    #CONSUMER_SECRET="XgXv9N8IF6pCjSCmtKFegYPDfxIcHWo8lZdRJNuf0jUExSAJsbOKtoSvAC9G9JhI"
    #replaced with live mpesa details 
    url="https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    CONSUMER_KEY="dvK5OJjyrB72m5OQTLPIlva150Pn7zw0hZNCFZXhpA5tKZLF"
    CONSUMER_SECRET="r8yjL9yLCjVU6ftDGHzRHrDfPW5jlKYVfPCyANoaCAyazx38oczdi9xh3GtYWgVd"
    basic=HTTPBasicAuth(CONSUMER_KEY,CONSUMER_SECRET)
    response=requests.get(
        url=url,
        auth=basic
    )
    if(response.status_code==200):
        data=response.json()
        token=data['access_token']
        return token
    else:
        return {'message':'failed to get the token'}

print(get_access_token())
def get_stk_push(phone_number,amount):

    token=get_access_token()
    url="https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp=datetime.now()
    timestampe=timestamp.strftime('%Y%m%d%H%M%S')
    #print(timestampe)

    #passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    passkey="b810df7928546cff0698cf6a80b44506048799fa64e96645ef7cf925f4ca35c7"
    shortcode="4002159"
    data=shortcode+passkey+timestampe
    
    password=base64.b64encode(data.encode('utf-8')).decode('utf-8')
    #print(password)
    body={
  "Password":password,
  "BusinessShortCode": shortcode,
  "Timestamp": timestampe,
  "Amount": int(amount),#the amount is an integer or the callback fails to indicate success status of 
  "PartyA": phone_number,
  "PartyB": shortcode,
  "TransactionType": "CustomerPayBillOnline",
  "PhoneNumber": phone_number,
  "TransactionDesc": "Test",
  "AccountReference": "Dhichiafis Tek System",
  "CallBackURL": "https://fastapi-stk-push-implementation.onrender.com/transactions/mpesa/callback"
}
    headers={
        "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    

    response=requests.post(
        url=url,
        json=body,
        headers=headers
    )
    return response.json()

def disburse_payments(phone_number,amount):
    #url="https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest"
    #replace with live url
    url="https://api.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
    #replace with live shortcode
    shortcode="4002159"
    body={
        "OriginatorConversationID": "a6351cf491ef493c831d82e337d4e2b4", 
    "InitiatorName": "TOchieng", 
    "SecurityCredential": "Fsg6mjxypAapmfDftSQce8Rqx1SbgWLAQtNqc5raZ7PS2WVF7kZ7TWZ96sza0rrYaXIAGys3K7MfaRqy/zLTzcJnVmzqpqSJuKnpJ8wbDXfWLCFW+4xYYaRRCPNp4vhuCCKfOzQxEPfQS53tvucvCvSSklcd9OePxu7ruUAZ/A1K8w4HmvNUsJgBZ2fGp4uxbVvDQWIPsrd+vjx9lXsA/MZJxZULunbPeh6Mu3tv8XrjgFy0fZdKJCzzyR/L407oEAY5EdkT3N2trX40+04/f6yYs8DsYUVgV7oUjTwUNC6X2/bU1jNJykmy87w2UriCPFVDi6seaixkQDLuQGwmqw==", 
    "CommandID": "BusinessPayment", 
    "Amount": int(amount), 
    "PartyA": shortcode, 
    "PartyB": phone_number, 
    "Remarks": "remarked", 
    "QueueTimeOutURL": "https://mydomain.com/path", 
    "ResultURL": "https://fastapi-stk-push-implementation.onrender.com/transactions/payment/callback", 
    "Occassion": "ChristmasPay" 
    }
    token=get_access_token()
    headers={
        "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    response=requests.post(
        url=url,
        json=body,
        headers=headers
    )
    if response.status_code==200:
        print(response.json())
    else:
        print('faild to post')

disburse_payments(254721676091,10)
#disburse_payments("254708374149")

def get_transaction_status(transaction_id):
    url="https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query"
    token=get_access_token()
    timestamp=datetime.now()
    timestampe=timestamp.strftime('%Y%m%d%H%M%S')
    #print(timestampe)

    passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    shortcode="174379"
    data=shortcode+passkey+timestampe
    
    password=base64.b64encode(data.encode('utf-8')).decode('utf-8')

    body={
        
    "Initiator": "testapiuser",
    #"SecurityCredential":password,
    "SecurityCredential": "ClONZiMYBpc65lmpJ7nvnrDmUe0WvHvA5QbOsPjEo92B6IGFwDdvdeJIFL0kgwsEKWu6SQKG4ZZUxjC",
    "Command ID": "TransactionStatusQuery",
    "Transaction ID": transaction_id,
    "OriginalConversationID": "7071-4170-a0e5-8345632bad442144258",
    "PartyA": "600782",
    "IdentifierType": "4",
    "ResultURL": "http://myservice:8080/transactionstatus/result",
    "QueueTimeOutURL": "http://myservice:8080/timeout",
    "Remarks": "OK",
    "Occasion": "OK"
    }
    headers={
        "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }
    response=requests.post(
        url=url,
        json=body,
        headers=headers
    )
    if(response.status_code==200):
        print(response.json())

