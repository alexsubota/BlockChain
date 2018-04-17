import elasticsearch
import json
import requests
from LedgerRipple import LedgerRipple

#init const
CONST_ELASTIC_URL = 'http://localhost:9200'
CONST_ELASTIC_MAXSIZE = 25
CONST_ELASTIC_TIMEOUT = 30
CONST_ELASTIC_MAXRETRIES = 10
CONST_ELASTIC_LEDGER_NAME = "ledger"
CONST_ELASTIC_TRANSACTION_NAME = "transaction"
CONST_RIPPLE_HEALTH_CHECK = 'https://data.ripple.com/v2/health/importer?verbose=true'
CONST_NULL_TRANSACTIONS = [{}]
CONST_NULL_LEDGER = {}

class ElasticRipple:
    
    def __init__(self):
        self.elasticDatabase = elasticsearch.Elasticsearch([CONST_ELASTIC_URL], maxsize = CONST_ELASTIC_MAXSIZE,
                                        timeout = CONST_ELASTIC_TIMEOUT, max_retries = CONST_ELASTIC_MAXRETRIES, 
                                        retry_on_timeout=True)
        self.indexRipple()
    
    #add ledger to elastic database (nulls are also added)
    def addLedger(self, LedgerObject, curID):
        self.elasticDatabase.index(index = CONST_ELASTIC_LEDGER_NAME, doc_type = 'b', body = LedgerObject, id = curID)
    
    #add transaction to elastic database (nulls are also added)
    def addTransactions(self, Transactions):
        if Transactions != CONST_NULL_TRANSACTIONS:
            for tx in Transactions:
                #drop some data (some data have different types)
                del tx['meta']['AffectedNodes']
                if 'TakerPays' in tx['tx'] and type(tx['tx']['TakerPays']) != 'dict':
                    del tx['tx']['TakerPays']
                if 'TakerGets' in tx['tx'] and type(tx['tx']['TakerGets']) != 'dict':
                    del tx['tx']['TakerGets']
                self.elasticDatabase.index(index = CONST_ELASTIC_TRANSACTION_NAME, doc_type = 'b', body = tx)
    
    #main function to index ripple data
    def indexRipple(self):
        self.getLastValidatedLedgerIndex()
        self.getCurrentLedgerIndex()
        while self.CurrentLedgerIndex <= self.LastValidatedLedgerIndex:
            self.CurrentLedgerIndex += 1
            self.RL = LedgerRipple(self.CurrentLedgerIndex)
            if self.RL.result == 'success':
                self.addTransactions(self.RL.Transactions)
                self.addLedger(self.RL.LedgerHeader, self.CurrentLedgerIndex)
            else:
                self.addTransactions(CONST_NULL_TRANSACTIONS)
                self.addLedger(CONST_NULL_LEDGER, self.CurrentLedgerIndex)
    
    #get current index of elastic database
    def getCurrentLedgerIndex(self):
        try:
            self.CurrentLedgerIndex = self.elasticDatabase.count(CONST_ELASTIC_LEDGER_NAME)['count']
        except:
            self.CurrentLedgerIndex = 0
    
    #get last index of ripple data(global)
    def getLastValidatedLedgerIndex(self):
        try:
            self.LastValidatedLedgerIndex = json.loads(requests.get(CONST_RIPPLE_HEALTH_CHECK).text)['last_validated_ledger']
        except:
            self.LastValidatedLedgerIndex = 1