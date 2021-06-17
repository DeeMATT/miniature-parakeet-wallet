import json
from api_utils.views import (
    badRequestResponse, resourceConflictResponse, internalServerErrorResponse, unAuthenticatedResponse,
    unAuthorizedResponse, successResponse, resourceNotFoundResponse, getUserIpAddress, paginatedResponse
)
from errors.views import getError, ErrorCodes
from django.utils import settings
from api_utils.validators import validateKeys
from .wallets_africa import WalletsAfricaAPI
from .utils import createUserWalletData

# instantiate
wallets_api = WalletsAfricaAPI()

# create wallets api key upon registering as tenant
# create wallets api key for members upon approval or admin signup


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
    _ = createUserWalletData(createdWalletData)

    return successResponse("Wallet created", createdWalletData)


def getSubWalletBalance(request):
    pass

def debitSubWalletFromMainWallet(request):
    pass

def creditSubWalletFromMainWallet(request):
    pass

def retrieveSubWalletTransactions(request):
    # add filter param for transaction type, default to all
    # add filter param for date range, (dateFrom, dateTo)
    # today, yesterday, last 7 days, this month, last 30 days, all time

    pass

def subWalletTransferToBankAcct(request):
    pass

def subWalletTransferToSubWallet(request):
    pass


