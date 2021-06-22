from .models import UserWalletData
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
import uuid



def createUserWalletData(data):
    try:
        object = UserWalletData.objects.create(
            first_name=data.get('FirstName'),
            last_name=data.get('LastName'),
            email_address=data.get('Email'),
            phone_number=data.get('PhoneNumber'),
            bvn=data.get('BVN'),
            birthday=data.get('DateOfBirth'),
            created_at=data.get('DateSignedup'),
            password=data.get('Password'),
            account_no=data.get('AccountNo'),
            bank_name=data.get('Bank'),
            account_name=data.get('AccountName'),
            available_balance=data.get('AvailableBalance'),
            wallet_key=str(uuid.uuid4())[:14].replace("-", '')
        )
        return object

    except Exception as err:
        logger.error("createUserWalletData@Error")
        logger.error(err)
        return None
