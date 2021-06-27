import requests
import logging
import json
from api_utils.views import (
    badRequestResponse, resourceConflictResponse, internalServerErrorResponse, unAuthenticatedResponse,
    unAuthorizedResponse, resourceNotFoundResponse
)
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)


class WalletsAfricaAPI:
    
    def __init__(self):
        self.base_url = settings.WALLETS_BASE_URL
        self.sandbox_url = settings.WALLETS_SANDBOX_URL
        self.secret_key = settings.WALLETS_SECRET_KEY
        self.public_key = settings.WALLETS_PUBLIC_KEY

    def _error_response(self, code, data):
        status_code = str(code)

        if status_code == "400":
            return badRequestResponse(data)
        if status_code == "401":
            return unAuthenticatedResponse(data)
        if status_code == "403":
            return unAuthorizedResponse(data)
        if status_code == "404":
            return resourceNotFoundResponse(data)
        if status_code == "409":
            return resourceConflictResponse(data)
        if status_code == "500":
            return internalServerErrorResponse(data)

        return badRequestResponse(data)

    def _wallet_api_request(self, endpoint, http_method, payload={}):
        try:
            method = http_method.upper()
            url = f"{self.base_url}/{endpoint}"
            header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.public_key}"
            }
            api_request = requests.request(method, url, headers=header, data=payload)
            response = api_request.json()
            
            if isinstance(response, dict):
                if 'ResponseCode' in response:
                    response_status_code = response['ResponseCode']
                else:
                    response_status_code = response['Response']['ResponseCode']
            else:
                response_status_code = api_request.status_code
                
            if int(response_status_code) not in range(200, 299):
                if isinstance(response, dict):
                    if 'Response' in response:
                        data = response['Response']
                    else:
                        data = response
                    return self._error_response(response_status_code, data), False
            else:
                if isinstance(response, dict):
                    data = response['Data']
                else:
                    data = response

            return data, True

        except Exception as e:
            logger.error("_wallet_api_request@Error")
            logger.error(e)
            return None, str(e)

    def check_balance(self, currency="NGN"):
        """
        This method is used to get the balance of the 
        developer wallet in different currencies
        """
        try:
            payload = json.dumps({
                "currency": currency,
                "secretKey": self.secret_key
            })
            
            response, msg = self._wallet_api_request("self/balance", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("check_balance@Error")
            logger.error(e)
            return None, str(e)

    def generate_wallet(self, first_name, last_name, email, birthday, phone_number, currency="NGN"):
        """
        Generate a wallet
        """
        try:
            payload = json.dumps({
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "dateOfBirth": birthday,
                "phoneNumber": phone_number,
                "currency": currency,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/generate", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("generate_wallet@Error")
            logger.error(e)
            return None, str(e)

    def debit_wallet(self, amount, phoneNumber, reference):
        """
        Perform a debit on a sub wallet and credit the main wallet
        """
        try:
            payload = json.dumps({
                "transactionReference": reference,
                "amount": float(amount),
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/debit", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("debit_wallet@Error")
            logger.error(e)
            return None, str(e)

    def credit_wallet(self, reference, amount, phoneNumber):
        """
        Perform a credit on a sub wallet
        """
        # str(uuid.uuid1()).replace("-", "")
        try:
            payload = json.dumps({
                "transactionReference": reference,
                "amount": float(amount),
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/debit", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("credit_wallet@Error")
            logger.error(e)
            return None, str(e)

    def set_wallet_password(self, password, phoneNumber):
        """
        Set Password for a subwallet
        """
        try:
            payload = json.dumps({
                "password": password,
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/password", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("set_wallet_password@Error")
            logger.error(e)
            return None, str(e)

    def set_wallet_pin(self, pin, phoneNumber):
        """
        Set Pin for a subwallet
        """
        try:
            payload = json.dumps({
                "transactionPin": pin,
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/pin", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("set_wallet_pin@Error")
            logger.error(e)
            return None, str(e)

    def get_wallet_transactions(self, pin, phoneNumber, dateFrom, dateTo, transactionType=0, take=1000000, skip=0, currency="NGN"):
        """
        Get list of transactions for a wallet
        """
        try:
            payload = json.dumps({
                "skip": skip,
                "take": take,
                "dateFrom": dateFrom,
                "dateTo": dateTo,
                "transactionType": transactionType,
                "phoneNumber": phoneNumber,
                "transactionPin": pin,
                "currency": currency,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/transactions", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("get_wallet_transactions@Error")
            logger.error(e)
            return None, str(e)

    def get_wallet_by_phone(self, phoneNumber):
        """
        Get a particular wallet using phone number
        """
        try:
            payload = json.dumps({
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/getuser", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("get_wallet_by_phone@Error")
            logger.error(e)
            return None, str(e)

    def get_wallet_by_email(self, email):
        """
        Get a particular wallet using email
        """
        try:
            payload = json.dumps({
                "email": email,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/getuser", "POST", payload)
            return response, msg, 
            
        except Exception as e:
            logger.error("get_wallet_by_phone@Error")
            logger.error(e)
            return None, str(e)

    def get_wallet_balance(self, phoneNumber, currency="NGN"):
        """
        Get wallet balance
        """
        try:
            payload = json.dumps({
                "phoneNumber": phoneNumber,
                "currency": currency,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/balance", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("get_wallet_balance@Error")
            logger.error(e)
            return None, str(e)

    def get_wallet_acct_number(self, phoneNumber):
        """
        Retrieve account number tied to a wallet
        """
        try:
            payload = json.dumps({
                "phoneNumber": phoneNumber,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("wallet/nuban", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("get_wallet_acct_number@Error")
            logger.error(e)
            return None, str(e)

    def get_all_banks(self):
        """
        Get transaction details about wallet to bank transfer
        """
        try:
            response, msg = self._wallet_api_request("transfer/banks/all", "POST")
            return response, msg
            
        except Exception as e:
            logger.error("get_bank_transfer_info@Error")
            logger.error(e)
            return None, str(e)

    def get_bank_transfer_info(self, reference):
        """
        Get transaction details about wallet to bank transfer
        """
        try:
            payload = json.dumps({
                "transactionReference": reference,
                "secretKey": self.secret_key
            })

            response, msg = self._wallet_api_request("transfer/bank/details", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("get_bank_transfer_info@Error")
            logger.error(e)
            return None, str(e)

    def bank_account_enquiry(self, bankCode, accountNumber):
        """
        Get Bank Account Information
        """
        try:
            payload = json.dumps({
                "SecretKey": self.secret_key,
                "BankCode": bankCode,
                "AccountNumber": accountNumber
            })

            response, msg = self._wallet_api_request("transfer/bank/account/enquire", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("bank_account_enquiry@Error")
            logger.error(e)
            return None, str(e)

    def bank_account_transfer(self, bankCode, accountNumber, amount, accountName, reference, description):
        """
        Transfer funds from a wallet to a bank account
        """
        try:
            payload = json.dumps({
                "SecretKey": self.secret_key,
                "BankCode": bankCode,
                "AccountNumber": accountNumber,
                "AccountName": accountName,
                "TransactionReference": reference,
                "Amount": amount,
                "Narration": description
            })

            response, msg = self._wallet_api_request("transfer/bank/account", "POST", payload)
            return response, msg
            
        except Exception as e:
            logger.error("bank_account_transfer@Error")
            logger.error(e)
            return None, str(e)
