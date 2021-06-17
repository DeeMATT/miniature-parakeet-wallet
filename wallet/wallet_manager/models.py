from django.db import models


class UserWalletData(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email_address = models.EmailField()
    phone_number = models.TextField()
    bvn = models.TextField(null=True)
    birthday = models.DateField()
    created_at = models.DateTimeField()

    password = models.TextField()
    account_no = models.TextField()
    bank_name = models.TextField()
    account_name = models.TextField()
    available_balance = models.TextField()
