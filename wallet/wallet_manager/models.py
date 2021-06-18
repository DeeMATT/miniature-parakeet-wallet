from django.db import models
import uuid


class UserWalletData(models.Model):
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    email_address = models.EmailField(null=True)
    phone_number = models.TextField(null=True)
    bvn = models.TextField(null=True)
    birthday = models.TextField(null=True)
    created_at = models.TextField(null=True)

    password = models.TextField(null=True)
    account_no = models.TextField(null=True)
    bank_name = models.TextField(null=True)
    account_name = models.TextField(null=True)
    available_balance = models.TextField(null=True)

    wallet_key = models.TextField(default=str(uuid.uuid4())[:14].replace("-", ''))
