from django.urls import path
from .views import (
    createSubWalletForUser, retrieveSubWalletTransactions, getWalletInfo, setWalletPin,
    subWalletTransferToBankAcct, getAllBanks, bankAccountEnquiry, debitSubWallet,
    creditSubWallet
    )

urlpatterns = [
    path('create', createSubWalletForUser),
    path('set-pin', setWalletPin),
    path('account/info', getWalletInfo),
    path('transactions', retrieveSubWalletTransactions),
    path('transfer/bank', subWalletTransferToBankAcct),
    path('transfer/bank/all', getAllBanks),
    path('transfer/account/validate', bankAccountEnquiry),
    path('debit', debitSubWallet),
    path('credit', creditSubWallet),
]