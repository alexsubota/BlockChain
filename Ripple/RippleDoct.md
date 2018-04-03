# <center>*Ripple*

## Ledger

Parts of ledger:
   1. A header - The **ledger index**, hashes of its other contents, and other metadata.
   2. A transaction tree - The **transactions** that were applied to the previous ledger to make this one. Transactions are the only way to change the ledger.
   3. A state tree - All the **ledger** objects that contain the settings, balances, and objects in the ledger as of this version

##### Header of ledger

| <center>Field          | <center>Type    | <center>Description |
|------------------------|-----------------|---------------------|
| ledger_index | String  | The sequence number of the ledger.    |
| ledger_hash  | String  | The SHA-512Half of the ledger header, excluding the ledger_hash itself.   |
| account_hash | String  | The SHA-512Half of this ledger's state tree information. |
|close_time    | Number  | The approximate time this ledger closed, as the number of seconds since the Ripple Epoch of 2000-01-01 00:00:00. This value is rounded based on the close_time_resolution|
|closed|Boolean| If true, this ledger version is no longer accepting new transactions.|
|parent_hash| String| The ledger_hash value of the previous ledger that was used to build this one.|
|total_coins| String| The total number of drops of XRP owned by accounts in the ledger. This omits XRP that has been destroyed by transaction fees. The actual amount of XRP in circulation is lower because some accounts are "black holes" whose keys are not known by anyone.|
|transaction_hash| String| The SHA-512Half of the transactions included in this ledger.|
|close_time_resolution| Number|An integer in the range [2,120] indicating the maximum number of seconds by which the close_time could be rounded.|
|close_flags| | A bit-map of flags relating to the closing of this ledger|

##### State tree

|<center>Type    | <center>Description|
|----------------|--------------------|
|AccountRoot| The settings, XRP balance, and other metadata for one account.|
|Amendments | Singleton object with status of enabled and pending amendments.|
|Check|A check that can be redeemed for money by its destination|
|DirectoryNode | Contains links to other objects.|
|Escrow | Contains XRP held for a conditional payment.|
|FeeSettings | Singleton object with consensus-approved base transaction cost and reserve requirements.|
|LedgerHashes | Lists of prior ledger versions' hashes for history lookup.|
|Offer | An offer to exchange currencies, known in finance as an order.|
|PayChannel | A channel for asynchronous XRP payments.|
|RippleState | Links two accounts, tracking the balance of one currency between them. The concept of a trust line is really an abstraction of this object type.|
|SignerList | A list of addresses for multi-signing transactions.|

###System requirement
For best performance in enterprise production environments, Ripple recommends running rippled on bare metal with the following characteristics:
- Operating System: Ubuntu 16.04+
- CPU: Intel Xeon 3+ GHz processor with 4 cores and hyperthreading enabled
- Disk: SSD
- RAM:
	- For testing: 8GB+
	- For production: 32GB
- Network: Enterprise data center network with a gigabit network interface on the host

##Transactions
###Common Field
| Field   | Type | Description|
|---------|------|------------|
| Account |  String | The unique address of the account that initiated the transaction.|
|AccountTxnID| String |	(Optional) Hash value identifying another transaction. This transaction is only valid if the sending account's previously-sent transaction matches the provided hash.|
|Fee|String|(Required, but auto-fillable) Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network.|
|Flags|Unsigned Integer|(Optional) Set of bit-flags for this transaction.|
|LastLedgerSequence	|Number|(Optional, but strongly recommended) Highest ledger sequence number that a transaction can appear in.|
|Memos|Array of Objects|(Optional) Additional arbitrary information used to identify this transaction.|
|Sequence|Unsigned Integer|	(Required, but auto-fillable) The sequence number, relative to the initiating account, of this transaction. A transaction is only valid if the Sequence number is exactly 1 greater than the last-valided transaction from the same account.|
|SigningPubKey|String|(Automatically added when signing) Hex representation of the public key that corresponds to the private key used to sign this transaction. If an empty string, indicates a multi-signature is present in the Signers field instead.|
|Signers|Array|(Optional) Array of objects that represent a multi-signature which authorizes this transaction.|
|SourceTag|Unsigned Integer|(Optional) Arbitrary integer used to identify the reason for this payment, or a sender on whose behalf this transaction is made. Conventionally, a refund should specify the initial payment's SourceTag as the refund payment's DestinationTag.|
|TransactionType|String|The type of transaction.|
|TxnSignature	|String|(Automatically added when signing) The signature that verifies this transaction as originating from the account it says it is from|
#####Memos
|Field	|Type	|Description|
|-------|-------|-----------|
|MemoData |String |Arbitrary hex value, conventionally containing the content of the memo.|
|MemoFormat	|String	|Hex value representing characters allowed in URLs. Conventionally containing information on how the memo is encoded, for example as a MIME type.|
|MemoType |String	|Hex value representing characters allowed in URLs. Conventionally, a unique relation (according to RFC 5988) that defines the format of this memo.|
#####Signers Field
|Field	|Type	|Description|
|-------|-------|-----------|
|Account |String |The address associated with this signature, as it appears in the SignerList.|
|TxnSignature |String |A signature for this transaction, verifiable using the SigningPubKey.|
|SigningPubKey |String |The public key used to create this signature.|

####Transaction Types
|Type|Description|
|----|-----------|
|AccountSet |Set options on an account|
|CheckCancel |Cancel a check|
|CheckCash |Redeem a check|
|CheckCreate |Create a check|
|EscrowCancel |Reclaim escrowed XRP|
|EscrowCreate |Create an escrowed XRP payment|
|EscrowFinish |Deliver escrowed XRP to recipient|
|OfferCancel |Withdraw a currency-exchange order|
|OfferCreate |Submit an order to exchange currency|
|Payment |Send funds from one account to another|
|PaymentChannelClaim |Claim money from a payment channel|
|PaymentChannelCreate |Open a new payment channel|
|PaymentChannelFund |Add more XRP to a payment channel|
|SetRegularKey |Set an account's regular key|
|SignerListSet |Set multi-signing settings|
|TrustSet |Add or modify a trust line|

##Ripple Data API
The Ripple Data API provides access to information about changes in the XRP Ledger, including transaction history and processed analytical data. This information is stored in a dedicated database, which frees rippled servers to keep fewer historical ledger versions.
#####Get Ledger
Retrieve a specific Ledger by hash, index, date, or latest validated.
`GET /v2/ledgers/{:identifier}`

|Field	|Value	|Description|
|-------|-------|-----------|
|ledger_identifier	|Ledger Hash, Ledger Index, or Timestamp	|(Optional) An identifier for the ledger to retrieve: either the full hash in hex, an integer sequence number, or a date-time. If a date-time is provided, retrieve the ledger that was most recently closed at that time. If omitted, retrieve the latest validated ledger.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-------|-------|-----------|
|transactions	|Boolean	|If true, include the identifying hashes of all transactions that are part of this ledger.|
|binary	|Boolean	|If true, include all transactions from this ledger as hex-formatted binary data. (If provided, overrides transactions.)
|expand	|Boolean	|If true, include all transactions from this ledger as nested JSON objects. (If provided, overrides binary and transactions.)

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-------|-------|-----------|
|result	|String	|The value success indicates that this is a successful response.|
|ledger	|Ledger object	|The requested ledger.|

Response:
200 OK
{
    "result": "success", 
    "ledger": {
        "ledger_hash": "3170da37ce2b7f045f889594cbc323d88686d2e90e8ffd2bbcd9bad12e416db5",
        "ledger_index": 8317037,
        "parent_hash": "aff6e04f07f441abc6b4133f8c50c65935b817a85b895f06dba098b3fbc1be90",
        "total_coins": 99999980165594400,
        "close_time_res": 10,
        "accounts_hash": "8ad73e49a34d8b9c31bc13b8a97c56981e45ee70225ef4892e8b198fec5a1f7d",
        "transactions_hash": "33e0b9c5fd7766343e67854aed4222f5ed9c9507e0ec0d7ae7d54d0f17adb98e",
        "close_time": 1408047740,
        "close_time_human": "2014-08-14T20:22:20+00:00"
    }
}`

#####Get Ledger Validations
Retrieve a any validations recorded for a specific ledger hash. This dataset includes ledger versions that are outside the validated ledger chain.
`GET /v2/ledgers/{:ledger_hash}/validations`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-------|-------|-----------|
|ledger_hash	|Hash	|Ledger hash to retrieve validations for.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-------|-------|-----------|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-------|-------|-----------|
|result	|String - success	|Indicates that the body represents a successful response.|
|ledger_hash	|String - Hash	|The identifying hash of the ledger version requested.|
|count	|Integer	|Number of validations returned.|
|marker	|String	(May be omitted) |Pagination marker.|
|validations	|Array of Validation Objects	|All known validation votes for the ledger version.|

Response:
200 OK
{
  "result": "success",
  "ledger_hash": "A10E9E338BA365D2B768814EC8B0A9A2D8322C0040735E20624AF711C5A593E7",
  "count": 2,
  "marker": "A10E9E338BA365D2B768814EC8B0A9A2D8322C0040735E20624AF711C5A593E7|n9KDJnMxfjH5Ez8DeWzWoE9ath3PnsmkUy3GAHiVjE7tn7Q7KhQ2|20160608001732",
  "validations": [
    {
      "count": 27,
      "first_datetime": "2016-06-08T00:17:32.352Z",
      "last_datetime": "2016-06-08T00:17:32.463Z",
      "ledger_hash": "A10E9E338BA365D2B768814EC8B0A9A2D8322C0040735E20624AF711C5A593E7",
      "reporter_public_key": "n9KJb7NMxGySRcjCqh69xEPMUhwJx22qntYYXsnUqYgjsJhNoW7g",
      "signature": "304402204C751D0033070EBC008786F0ECCA8E29195FD7DD8D22498EB6E4E732905FC7090220091F458976904E7AE4633A1EC405175E6A126798E4896DD452853B887B1E6359",
      "validation_public_key": "n949f75evCHwgyP4fPVgaHqNHxUVN15PsJEZ3B3HnXPcPjcZAoy7"
    },
    {
      "count": 3,
      "first_datetime": "2016-06-08T00:17:32.653Z",
      "last_datetime": "2016-06-08T00:17:32.673Z",
      "ledger_hash": "A10E9E338BA365D2B768814EC8B0A9A2D8322C0040735E20624AF711C5A593E7",
      "reporter_public_key": "n9JCK5AML7Ejv3TcJmnvJk5qeYhf7Q9YwScjz5PhtUbtWCKH3NAm",
      "signature": "3045022100A48E5AF6EA9D0ACA6FDE18536081A7D2182535579EA580C3D0B0F18C2556C5D30220521615A3D677376069F8F3E608B59F14482DDE4CD2A304DE578B6CCE2F5E8D54",
      "validation_public_key": "n9K6YbD1y9dWSAG2tbdFwVCtcuvUeNkBwoy9Z6BmeMra9ZxsMTuo"
    }
  ]
}

##Get Ledger Validation
Retrieve a validation vote recorded for a specific ledger hash by a specific validator. This dataset includes ledger versions that are outside the validated ledger chain.
`GET /v2/ledgers/{:ledger_hash}/validations/{:pubkey}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|--|--|--|
|ledger_hash	|Hash	|Ledger hash to retrieve validations for.|
|pubkey	|String - Base-58 Public Key	|Validator public key.|

Response:
200 OK
{
  "count": 27,
  "first_datetime": "2016-06-08T00:17:32.352Z",
  "last_datetime": "2016-06-08T00:17:32.463Z",
  "ledger_hash": "A10E9E338BA365D2B768814EC8B0A9A2D8322C0040735E20624AF711C5A593E7",
  "reporter_public_key": "n9KJb7NMxGySRcjCqh69xEPMUhwJx22qntYYXsnUqYgjsJhNoW7g",
  "signature": "304402204C751D0033070EBC008786F0ECCA8E29195FD7DD8D22498EB6E4E732905FC7090220091F458976904E7AE4633A1EC405175E6A126798E4896DD452853B887B1E6359",
  "validation_public_key": "n949f75evCHwgyP4fPVgaHqNHxUVN15PsJEZ3B3HnXPcPjcZAoy7",
  "result": "success"
}