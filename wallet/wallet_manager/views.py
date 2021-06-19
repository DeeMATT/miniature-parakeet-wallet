import json
from api_utils.views import (
    badRequestResponse, resourceConflictResponse, internalServerErrorResponse, unAuthenticatedResponse,
    unAuthorizedResponse, successResponse, resourceNotFoundResponse, paginatedResponse
)
from errors.views import getError, ErrorCodes
from django.conf import settings
from api_utils.validators import validateKeys
from .wallets_africa import WalletsAfricaAPI
from .utils import createUserWalletData
from .models import UserWalletData
from datetime import date, timedelta
from django.core.paginator import Paginator
from dateutil.parser import parse
import uuid

# instantiate
wallets_api = WalletsAfricaAPI()

# create wallets api key upon registering as tenant
# create wallets api key for members upon approval or admin signup

def getWalletUsingKey(secretKey):
    try:
        wallet = UserWalletData.objects.get(wallet_key=secretKey)
        return wallet
    
    except UserWalletData.DoesNotExist:
        return None


def createSubWalletForUser(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)
    # verify that the calling user has a valid secret
    secret = request.headers.get('Secret')
    if secret != settings.ROOT_SECRET:
        return badRequestResponse(getError(ErrorCodes.INVALID_CREDENTIALS, "Invalid Secret specified in the request headers"))

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['first_name', 'last_name', 'email', 'birthday', 'phone_number'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    first_name = body['first_name']
    last_name = body['last_name']
    email = body['email']
    birthday = body['birthday']
    phone_number = body['phone_number']

    # check if sub wallet exists for phone number passed
    existingWalletByPhone, msg = wallets_api.get_wallet_by_phone(phone_number)
    if existingWalletByPhone == None:
        return internalServerErrorResponse  (getError(ErrorCodes.GENERIC_ERROR, msg))
    elif msg:
        return resourceConflictResponse(getError(ErrorCodes.GENERIC_ERROR, "Wallets Already Exist for the Phone number specified"))

    # check if sub wallet exists for email passed
    existingWalletByEmail, msg = wallets_api.get_wallet_by_email(email)
    if existingWalletByEmail == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    elif msg:
        return resourceConflictResponse(getError(ErrorCodes.GENERIC_ERROR, "Wallets Already Exist for the Phone number specified"))

    # generate sub-wallet
    createdWalletData, outcome = wallets_api.generate_wallet(first_name, last_name, email, birthday, phone_number)
    if createdWalletData == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, outcome))
    if not outcome:
        # the request failed
        return createdWalletData

    # create reference on our model
    user_wallet = createUserWalletData(createdWalletData)
    wallet_key = user_wallet.wallet_key

    return successResponse("Wallet created", body={"wallet_key": wallet_key})

def setWalletPin(request):
    # make sure to set initial_wallet_pin_changed attribute

    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['secret_key', 'pin', 'email_address'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    secretKey = body['secret_key']
    pin = body['pin']
    email_address = body['email_address']

    # validate secret key
    existingWallet = getWalletUsingKey(secretKey)
    if not existingWallet:
        return badRequestResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "No wallet exists for the specified secret key"))
    elif existingWallet.email_address != email_address:
        return unAuthorizedResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "The email specified isn't associated with the wallet for secret key"))
    
    phone_number = existingWallet.phone_number

    # change wallet pin
    pinChange, msg = wallets_api.set_wallet_pin(pin, phone_number)

    if pinChange == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return pinChange

    return successResponse("Wallet pin", body={})

def getSubWalletBalance(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['secret_key', 'email_address'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    secretKey = body['secret_key']
    email_address = body['email_address']

    # validate secret key
    existingWallet = getWalletUsingKey(secretKey)
    if not existingWallet:
        return badRequestResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "No wallet exists for the specified secret key"))
    elif existingWallet.email_address != email_address:
        return unAuthorizedResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "The email specified isn't associated with the wallet for secret key"))

    phone_number = existingWallet.phone_number
    # get wallet balance
    balance, msg = wallets_api.get_wallet_balance(phone_number)
    if balance == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return balance

    return successResponse("Wallet balance", body=balance)

def debitSubWalletFromMainWallet(request):
    pass

def creditSubWalletFromMainWallet(request):
    pass

def getWalletInfo(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['secret_key', 'email_address', 'pin'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    secretKey = body['secret_key']
    email_address = body['email_address']
    pin = body['pin']

    # validate secret key
    existingWallet = getWalletUsingKey(secretKey)
    if not existingWallet:
        return badRequestResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "No wallet exists for the specified secret key"))
    elif existingWallet.email_address != email_address:
        return unAuthorizedResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "The email specified isn't associated with the wallet for secret key"))
    
    phone_number = existingWallet.phone_number

    # get wallet transactions
    date_to = str(date.today())  
    date_from = str(parse(existingWallet.created_at).date())
    transaction_type=0
    
    transactions, msg = wallets_api.get_wallet_transactions(pin, phone_number, date_from, date_to, transaction_type)
    if transactions == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return transactions

    transactions = transactions['Transactions']
    totalDebitAmount = 0
    totalCreditAmount = 0
    for data in transactions:
        if data['Type'] == "Credit":
            totalDebitAmount += data['Amount']
        if data['Type'] == "Debit":
            totalCreditAmount = data['Amount']

    # get user data
    walletByEmail, msg = wallets_api.get_wallet_by_email(email_address)
    if walletByEmail == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    elif msg:
        return resourceConflictResponse(getError(ErrorCodes.GENERIC_ERROR, "Wallets Already Exist for the Phone number specified"))
    
    currentBalance = walletByEmail.get("AvailableBalance")
    walletData = {
        "firstName": walletByEmail.get("FirstName"),
        "lastName": walletByEmail.get("LastName"),
        "emailAddress": walletByEmail.get("Email"),
        "phoneNumber": walletByEmail.get("PhoneNumber"),
        "walletCreationDate": walletByEmail.get("DateSignedup"),
        "walletAccountNumber": walletByEmail.get("AccountNo"),
        "walletAccountName": walletByEmail.get("AccountName"),
        "walletBank": walletByEmail.get("Bank"),
        "walletAvailableBalance": walletByEmail.get("AvailableBalance")
    }
        
    response_data = {
        "currentBalance": currentBalance,
        "totalMoneyReceived": totalCreditAmount,
        "totalMoneySpent": totalDebitAmount,
        "walletInfo": walletData
    }
        
    return successResponse("Wallet Information", body=response_data)

def retrieveSubWalletTransactions(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['secret_key', 'email_address', 'pin'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    secretKey = body['secret_key']
    email_address = body['email_address']
    pin = body['pin']

    # validate secret key
    existingWallet = getWalletUsingKey(secretKey)
    if not existingWallet:
        return badRequestResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "No wallet exists for the specified secret key"))
    elif existingWallet.email_address != email_address:
        return unAuthorizedResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "The email specified isn't associated with the wallet for secret key"))
    
    phone_number = existingWallet.phone_number

    queryDict = request.GET
    date_from = date_from = str(parse(existingWallet.created_at).date())
    date_to = str(date.today())  
    transaction_type = 0
    # transaction type code --- Credit = 1, Debit = 2, All = 0 or 3
    if 'transaction_type' in queryDict:
        try:
            transaction_type = int(queryDict.get('transaction_type'))
            if transaction_type not in (0, 1, 2, 3):
                return badRequestResponse(ErrorCodes.GENERIC_INVALID_PARAMETERS, message="TransactionType param must be any of <<0, 1, 2, 3>>")
            
        except Exception as e:
            return badRequestResponse(ErrorCodes.GENERIC_INVALID_PARAMETERS, message="TransactionType param shuld be a number")

    if 'day' in queryDict:
        try:
            day = queryDict.get('day')
            if day == 'all':
                date_from = str(parse(existingWallet.created_at).date())
            elif day == 'month':
                day = date.today().day - 1
                date_from = date.today() - timedelta(days=day)
            else:
                day = int(day)
                date_from = str(date.today() - timedelta(days=day))
        except Exception as e:
            return badRequestResponse(ErrorCodes.GENERIC_INVALID_PARAMETERS, message="Day param shuld be any of <<0, 1, 7, 30, month or all>>")

    # retrieve wallet transactions
    transactions, msg = wallets_api.get_wallet_transactions(pin, phone_number, date_from, date_to, transaction_type)
    if transactions == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return transactions

    transactions = transactions['Transactions']

    # Paginate the retrieved transaction
    if queryDict.get('pageBy'):
        pageBy = request.GET.get('pageBy')
    else:
        pageBy = 10

    paginator = Paginator(transactions, pageBy)

    if queryDict.get('page'):
        pageNum = request.GET.get('page')
    else:
        pageNum = 1

    # try if the page requested exists or is empty
    try:
        transactions = paginator.page(pageNum)

        paginationDetails = {
            "totalPages": paginator.num_pages,
            "limit": pageBy,
            "count": paginator.count,
            "currentPage": pageNum
        }
    except Exception as e:
        print(e)
        transactions = []
        paginationDetails = {}

    return paginatedResponse("Wallet transactions", body=transactions, pagination=paginationDetails)

def subWalletTransferToBankAcct(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['secret_key', 'email_address', 'bank_code', 'account_number', 'amount', 'account_name', 'description'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    secretKey = body['secret_key']
    email_address = body['email_address']
    bank_code = body['bank_code']
    account_number = body['account_number']
    amount = body['amount']
    account_name = body['account_name']
    description = body['description']

    # validate secret key
    existingWallet = getWalletUsingKey(secretKey)
    if not existingWallet:
        return badRequestResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "No wallet exists for the specified secret key"))
    elif existingWallet.email_address != email_address:
        return unAuthorizedResponse(getError(ErrorCodes.UNAUTHORIZED_REQUEST, "The email specified isn't associated with the wallet for secret key"))

    phone_number = existingWallet.phone_number
    # get wallet balance
    balance, msg = wallets_api.get_wallet_balance(phone_number)

    if balance == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return balance

    if balance['WalletBalance'] >= amount:
        # debit wallet
        debit_reference = str(uuid.uuid4())[:12]
        debit, msg = wallets_api.debit_wallet(amount, phone_number, debit_reference)
        if debit == None:
            return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
        if not msg:
            # the request failed
            return debit

    # exceute transfer
    transfer_reference = str(uuid.uuid4())[:12]
    transfer, msg = wallets_api.bank_account_transfer(bank_code, account_number, amount, account_name, transfer_reference, description)
    if transfer == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return transfer

    return successResponse("Wallet to Bank Account Transfer", body=transfer)

def subWalletTransferToSubWallet(request):
    pass

def getAllBanks(request):
    if request.method != "GET":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be GET"))

    all_banks, msg = wallets_api.get_all_banks()
    if all_banks == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return all_banks

    return successResponse("All Banks", body=all_banks)

def bankAccountEnquiry(request):
    if request.method != "POST":
        return badRequestResponse(getError(ErrorCodes.GENERIC_ERROR, "HTTP method should be POST"))

    body = json.loads(request.body)

    # check if required fields are present in request payload
    missingKeys = validateKeys(payload=body, requiredKeys=['bank_code', 'account_number'])
    if missingKeys:
        return badRequestResponse(getError(ErrorCodes.MISSING_FIELDS, f"The following key(s) are missing in the request payload: {missingKeys}"))
    
    bank_code = body['bank_code']
    account_number = body['account_number']

    bank_account, msg = wallets_api.bank_account_enquiry(bank_code, account_number)
    if bank_account == None:
        return internalServerErrorResponse(getError(ErrorCodes.GENERIC_ERROR, msg))
    if not msg:
        # the request failed
        return bank_account

    return successResponse("Bank Account Enquiry", body=bank_account)
