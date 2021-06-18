from django.urls import path
from .views import (
    createSubWalletForUser, retrieveSubWalletTransactions, getSubWalletBalance, setWalletPin,
    retrieveSubWalletSpending, subWalletTransferToBankAcct, getAllBanks
    )

urlpatterns = [
    path('create', createSubWalletForUser),
    path('set-pin', setWalletPin),
    path('balance', getSubWalletBalance),
    path('transactions', retrieveSubWalletTransactions),
    path('transactions/aggregate', retrieveSubWalletSpending),
    path('transfer/bank', subWalletTransferToBankAcct),
    path('transfer/bank/all', getAllBanks)

]