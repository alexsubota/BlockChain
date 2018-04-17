import json
import requests

#const init
CONST_RIPPLE_URL = 'https://data.ripple.com/v2/'

class LedgerRipple:
    
    def __init__(self, LedgerIndex):
        requestResult = self.makeGetLedgerRequest(LedgerIndex)
        if requestResult['result'] == 'success':
            self.result = 'success'
            self.extract(requestResult['ledger'])
        else:
            self.result = 'error'

    #requets to get Ledger Data    
    @staticmethod
    def makeGetLedgerRequest(LedgerIndex):
        requestResult = json.loads(requests.get(CONST_RIPPLE_URL + 'ledgers/' + str(LedgerIndex) 
                                   + '?transactions=true&binary=false&expand=true').text)
        return requestResult

    #divide header of ledger and transactions
    def extract(self, LedgerObject):
        self.Transactions = LedgerObject.pop('transactions')
        self.LedgerHeader = LedgerObject