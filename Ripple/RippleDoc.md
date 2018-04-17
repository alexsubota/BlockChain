# <center>*Ripple*

## Contents
- Introduction
- System requirement
- Object types
- Data API
- How to use drain

## Introduction

The Ripple Data API provides access to information about changes in the XRP Ledger, including transaction history and processed analytical data. This information is stored in a dedicated database, which frees rippled servers to keep fewer historical ledger versions.

Ripple provides a live instance of the Data API with as complete a transaction record as possible at the following address:

[https://data.ripple.com](https://data.ripple.com)

## System requirement

For best performance in enterprise production environments, Ripple recommends running rippled on bare metal with the following characteristics:
- Operating System: Ubuntu 16.04+
- CPU: Intel Xeon 3+ GHz processor with 4 cores and hyperthreading enabled
- Disk: SSD
- RAM:
	- For testing: 8GB+
	- For production: 32GB
- Network: Enterprise data center network with a gigabit network interface on the host

## Object types

### Ledger

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

## Transactions

### Common Field

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

##### Memos

|Field	|Type	|Description|
|-------|-------|-----------|
|MemoData |String |Arbitrary hex value, conventionally containing the content of the memo.|
|MemoFormat	|String	|Hex value representing characters allowed in URLs. Conventionally containing information on how the memo is encoded, for example as a MIME type.|
|MemoType |String	|Hex value representing characters allowed in URLs. Conventionally, a unique relation (according to RFC 5988) that defines the format of this memo.|

##### Signers Field

|Field	|Type	|Description|
|-------|-------|-----------|
|Account |String |The address associated with this signature, as it appears in the SignerList.|
|TxnSignature |String |A signature for this transaction, verifiable using the SigningPubKey.|
|SigningPubKey |String |The public key used to create this signature.|

#### Transaction Types

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

### Basic Types

As a REST API, the Data API v2 uses JSON's native datatypes to represent API fields, with some special cases.

##### Numbers and Precision

XRP Ledger APIs generally use strings, rather than native JSON numbers, to represent numeric amounts of currency for both XRP and issued currencies. This protects against a loss of precision when using JSON parsers, which may automatically try to represent all JSON numbers in a floating-point format. Within the String value, the numbers are serialized in the same way as native JSON numbers:

- Base-10.
- Non-zero-prefaced.
- May contain `.` as a decimal point. For example, ½ is represented as 0.5. (American style, not European)
- May contain `E` or `e` to indicate being raised to a power of 10 (scientific notation). For example, `1.2E5` is equivalent to `1.2×105`, or `120000`.
- No comma (`,`) characters are used.

The precision for amounts of non-XRP currency in the XRP Ledger is as follows:

- Minimum nonzero absolute value: `1000000000000000e-96`
- Maximum value: `9999999999999999e80`
- Minimum value: `-9999999999999999e80`
- 15 decimal digits of precision

XRP has a different internal representation, and its precision is different:

- Minimum value: `0`
- Maximum value: `100000000000` (`1e11`)
- Precise to the nearest `0.000001` (`1e-6`)

In other words, XRP has the same precision as a 64-bit unsigned integer where each unit is equivalent to 0.000001 XRP.

##### Addresses

Accounts in the XRP Ledger are identified by a base58 XRP Ledger Address. The address is derived from the account's master public key, which is in turn derived from a secret key. An address is represented as a string in JSON and has the following characteristics:

- Between 25 and 35 characters in length
- Starts with the character `r`
- Uses alphanumeric characters, excluding the number "`0`" capital letter "`O`", capital letter "`I`", and lowercase letter "`l`"
- Case-sensitive
- Includes a 4-byte checksum so that the probability of generating a valid address from random characters is approximately `1` in `2^32`

##### Public Keys

The XRP Ledger uses public keys to verify cryptographic signatures in several places:

- To authorize transactions, a public key is attached to the transaction. The public key must be mathematically associated with the sending XRP Ledger address or the sender's regular key address.
- To secure peer-to-peer communications between rippled servers. This uses a "node public key" that the server generates randomly when it starts with an empty database.
- To sign validation votes as part of the consensus process. This uses a "validator public key" that the server operator defines in the config file.

Validator public keys and node public keys use the exact same format.

Public keys can be represented in hexadecimal or in base-58. In hexadecimal, all three types of public keys are 33 bytes (66 characters) long.

In base-58 format, validator public keys and node public keys always start with the character n, commonly followed by the character `9`. A validator public key in base-58 format can be up to 53 characters long. Example node public key: `n9Mxf6qD4J55XeLSCEpqaePW4GjoCR5U1ZeGZGJUCNe3bQa4yQbG`.

XRP Ledger addresses are mathematically associated with a public key. This public key is rarely encoded in base-58, but when it is, it starts with the character `a`.

#### Hashes

Many objects in the XRP Ledger, particularly transactions and ledgers, are uniquely identified by a 256-bit hash value. This value is typically calculated as a "SHA-512Half", which calculates a SHA-512 hash from some contents, then takes the first 64 characters of the hexadecimal representation. Since the hash of an object is derived from the contents in a way that is extremely unlikely to produce collisions, two objects with the same hash can be considered the same.

An XRP Ledger hash value has the following characteristics:

- Exactly 64 characters in length
- Hexadecimal character set: 0-9 and A-F.
- Typically written in upper case.

*SHA-512Half has similar security to the officially-defined SHA-512/256 hash function. However, the XRP Ledger's usage predates SHA-512/256 and is also easier to implement on top of an existing SHA-512 function. (As of this writing, SHA-512 support in cryptographic libraries is much more common than for SHA-512/256.)*

##### Timestamps

All dates and times are written in ISO 8601 Timestamp Format, using UTC. This format is summarized as:

`YYYY-MM-DDThh:mm:ssZ`

- Four-digit year
- Two-digit month
- Two-digit day
- The letter `T` separating the date part and the time part
- Two-digit hour using a 24-hour clock
- Two digit minute
- The letter `Z` indicating zero offset from UTC.

##### Ledger Index

A ledger index is a 32-bit unsigned integer used to identify a ledger. The ledger index is also known as the ledger's sequence number. The very first ledger was ledger index 1, and each new ledger has a ledger index 1 higher than that of the ledger immediately before it.

The ledger index indicates the order of the ledgers; the Hash value identifies the exact contents of the ledger. Two ledgers with the same hash are always the same. For validated ledgers, hash values and sequence numbers are equally valid and correlate 1:1. However, this is not true for in-progress ledgers:

- Two different rippled servers may have different contents for a current ledger with the same ledger index, due to latency in propagating transactions throughout the network.
- There may be multiple closed ledger versions competing to be validated by consensus. These ledger versions have the same sequence number but different contents (and different hashes). Only one of these closed ledgers can become validated.
- A current ledger's contents change over time, which would cause its hash to change, even though its ledger index number stays the same. The hash of a ledger is not calculated until the ledger is closed.

##### Account Sequence

A Sequence number is a 32-bit unsigned integer used to identify a transaction or Offer relative to a specific account.

Every account object in the XRP Ledger has a Sequence number, which starts at 1. For a transaction to be relayed to the network and possibly included in a validated ledger, it must have a Sequence field that matches the sending account's current Sequence number. An account's Sequence field is incremented whenever a transaction from that account is included in a validated ledger (regardless of whether the transaction succeeded or failed). This preserves the order of transactions submitted by an account, and differentiates transactions that would otherwise be the same.

Every Offer node in the XRP Ledger is marked with the sending `Account` `Address` and the `Sequence` value of the OfferCreate transaction that created it. These two fields, together, uniquely identify the Offer.

##### Currency Code

There are two kinds of currency code in the XRP Ledger:

- Three-character currency code. We recommend using all-uppercase ISO 4217 Currency Codes. However, any combination of the following characters is permitted: all uppercase and lowercase letters, digits, as well as the symbols `?`, `!`, `@`, `#`, `$`, `%`, `^`, `&`, `*`, `<`, `>`, `(`, `)`, `{`, `}`, `[`, `]`, and `|`. The currency code `XRP` (all-uppercase) is reserved for XRP and cannot be used by issued currencies.
- 160-bit hexadecimal values, such as `0158415500000000C1F76FF6ECB0BAC600000000`, according to the XRP Ledger's internal Currency Format. This representation is uncommon.

### Pagination

Many queries may return more data than is reasonable to return in a single HTTP response. The Data API uses a "limit and marker" system to control how much is returned in a single response ("page") and to query for additional content.

The `limit` query parameter to many requests restricts the response to a specific number of results in the response. The types of results and default values vary based on the method. For most methods, the limit is **200** by default, and can be set as high as **1000**. If you specify a `limit` larger than the maximum, the API uses the maximum value instead.

When a query has additional objects that are not contained in the current response, the JSON response contains a top-level field `marker` which indicates that you can retrieve additional results. To do so, make more requests with the previous value of the `marker` field as the `marker` query parameter. For each additional request, use the same parameters as the first request (except `marker`). When the response omits the `marker` parameter, that indicates that you have reached the end of the queryable data.

When a `marker` is or would be present, the response contains a `Link header` with `rel="next"`. This is a full URL to the next page of results. You can use this to paginate over results when the response is in `csv` format instead of `json`.

### Transaction Objects

Transactions have two formats - a compact "binary" format where the defining fields of the transaction are encoded as strings of hex, and an expanded format where the defining fields of the transaction are nested as complete JSON objects.

##### Full JSON Format

|Field  |Value  |Description|
|-|-|-|
|hash |String - Hash  |An identifying hash value unique to this transaction, as a hex string.|
|date |String - Timestamp |The time when this transaction was included in a validated ledger.
|ledger_index |Number - Ledger Index  |The sequence number of the ledger that included this ledger.|
|tx |Object |The fields of this transaction object, as defined by the Transaction Format|
|meta |Object |Metadata about the results of this transaction.|

##### Binary Format

|Field  |Value  |Description|
|-|-|-|
|hash |String - Hash  |An identifying hash value unique to this transaction, as a hex string.|
|date |String - Timestamp |The time when this transaction was included in a validated ledger.|
|ledger_index |Number - Ledger Index  |The sequence number of the ledger that included this ledger.|
|tx |String |The binary data that represents this transaction, as a hexadecimal string.
|meta |String |The binary data that represents this transaction's metadata, as a hex string.|

### Ledger Objects

A "ledger" is one version of the shared global ledger. Each ledger object has the following fields:

|Field  |Value  |Description|
|-|-|-|
|ledger_hash  |String - Hash  |An identifying hash unique to this ledger, as a hex string.|
|ledger_index |Number - Ledger Index  |The sequence number of the ledger. Each new ledger has a ledger index 1 higher than the ledger that came before it.|
|parent_hash  |String - Hash  |The identifying hash of the previous ledger.|
|total_coins  |String - Number  |The total number of "drops" of XRP still in existence at the time of the ledger. (Each XRP is 1,000,000 drops.)|
|close_time_res |Number |The ledger close time is rounded to this many seconds.|
|accounts_hash  |String - Hash  |Hash of the account information contained in this ledger, as hex.|
|transactions_hash  |String - Hash  |Hash of the transaction information contained in this ledger, as hex.|
|close_time |Number |When this ledger was closed, in UNIX time.|
|close_time_human |String - Timestamp |When this ledger was closed.|

*Ledger close times are approximate, typically rounded to about 10 seconds. Two ledgers could have the same `close_time` values, when their actual close times were several seconds apart. The sequence number (`ledger_index`) of the ledger makes it unambiguous which ledger closed first.*

##### Genesis Ledger

Due to a mishap early in the XRP Ledger's history, ledgers 1 through 32569 were lost. Thus, ledger #32570 is the earliest ledger available anywhere. For purposes of the Data API v2, ledger #32570 is considered the genesis ledger.

### Account Creation Objects

An account creation object represents the action of creating an account in the XRP Ledger. There are two variations, depending on whether the account was already present in ledger 32570, the earliest ledger available. Accounts that were already present in ledger 32570 are termed genesis accounts.

|Field  |Value  |Description|
|-|-|-|
|address  |String - Address |The identifying address of this account, in base-58.|
|inception  |String - Timestamp |The UTC timestamp when the address was funded. For genesis accounts, this is the timestamp of ledger 32570.|
|ledger_index |Number - Ledger Index  |The sequence number of the ledger when the account was created, or 32570 for genesis accounts.|
|parent |String - Address |(Omitted for genesis accounts) The address that provided the XRP to fund this address.|
|tx_hash  |String - Hash  |(Omitted for genesis accounts) The identifying hash of the transaction that funded this account.|
|initial_balance  |String - Number  |(Omitted for genesis accounts) The amount of XRP that funded this account.|
|genesis_balance  |String - Number  |(Genesis accounts only) The amount of XRP this account held as of ledger #32570.|
|genesis_index  |Number - Sequence Number |(Genesis accounts only) The transaction sequence number of the account as of ledger #32570|

### Exchange Objects

An exchange object represents an actual exchange of currency, which can occur in the XRP Ledger as the result of executing either an OfferCreate transaction or a Payment transaction. In order for currency to actually change hands, there must be a previously-unfilled Offer previously placed in the ledger with an OfferCreate transaction.

A single transaction can cause several exchanges to occur. In this case, the sender of the transaction is the taker for all the exchanges, but each exchange has a different provider, currency pair, or both.

|Field  |Value  |Description|
|-|-|-|
|base_amount  |Number |The amount of the base currency that was traded.
|counter_amount |Number |The amount of the counter currency that was traded.
|rate |Number |The amount of the counter currency acquired per 1 unit of the base currency.|
|autobridged_currency |String - Currency Code (May be omitted) If the offer was autobridged (XRP order books were used to bridge two non-XRP currencies), this is the other currency from the offer that executed this exchange.|
|autobridged_issuer |String - Address |(May be omitted) If the offer was autobridged (XRP order books were used to bridge two non-XRP currencies), this is the other currency from the offer that executed this exchange.|
|base_currency  |String - Currency Code |The base currency.|
|base_issuer  |String - Address |(Omitted for XRP) The account that issued the base currency.|
|buyer  |String - Address |The account that acquired the base currency.|
|client |String |(May be omitted) If the transaction contains a memo indicating what client application sent it, this is the contents of the memo.|
|counter_currency |String - Currency Code |The counter currency.|
|counter_issuer |String - Address |(Omitted for XRP) The account that issued the counter currency.|
|executed_time  |String - Timestamp |The time the exchange occurred.|
|ledger_index |Number - Ledger Index  |The sequence number of the ledger that included this transaction.|
|offer_sequence |Number - Sequence Number |The sequence number of the provider's existing offer in the ledger.|
|provider |String - Address |The account that had an existing Offer in the ledger.|
|seller |String - Address |The account that acquired the counter currency.|
|taker  |String - Address |The account that sent the transaction which executed this exchange.|
|tx_hash  |String - Hash  |The identifying hash of the transaction that executed this exchange. (Note: This exchange may be one of several executed in a single transaction.)
|tx_type  |String |The type of transaction that executed this exchange, either Payment or OfferCreate.|

### Reports Objects

Reports objects show the activity of a given account over a specific interval of time, typically a day. Reports have the following fields:

|Field  |Value  |Description|
|-|-|-|
|account  String - Address  The address of the account to which this report pertains.
|date |String - Timestamp |The start of the interval to which this report pertains.|
|high_value_received  |String - Number  |Largest amount received in a single transaction, normalized to XRP (as closely as possible). This includes payments and exchanges.|
|high_value_sent  |String - Number  |The largest amount sent in a single transaction, normalized to XRP (as closely as possible).|
|payments |Array of Payment Summary Objects |(May be omitted) Array with information on each payment sent or received by the account during this interval.|
|payments_received  |Number |The number of payments sent to this account. (This only includes payments for which this account was the destination, not payments that only rippled through the account or consumed the account's offers.)|
|payments_sent  |Number |The number of payments sent by this account.|
|receiving_counterparties |Array or Number  |If account lists requested, an array of addresses that received payments from this account. Otherwise, the number of different accounts that received payments from this account.|
|sending_counterparties |Array or Number  |If account lists requested, an array of addresses that sent payments to this account. Otherwise, the number of different accounts that sent payments to this account.|
|total_value  |String - Number  |Sum of total value received and sent in payments, normalized to XRP (as closely as possible).|
|total_value_received |String - Number  |Sum value of all payments to this account, normalized to XRP (as closely as possible).|
|total_value_sent |String - Number  |Sum value of all payments from this account, normalized to XRP (as closely as possible).|

### Payment Summary Objects

A Payment Summary Object contains a reduced amount of information about a single payment from the perspective of either the sender or receiver of that payment.

|Field  |Value  |Description|
|-|-|-|
|tx_hash  |String - Hash  |The identifying hash of the transaction that caused the payment.|
|delivered_amount |String - Number  |The amount of the destination `currency` actually received by the destination account.|
|currency |String - Currency |Code  The currency delivered to the recipient of the transaction.|
|issuer |String - Address |The gateway issuing the currency, or an empty string for XRP.|
|type |String |Either `sent` or `received`, indicating whether the perspective account is sender or receiver of this transaction.|

### Payment Objects

In the Data API, a Payment Object represents an event where one account sent value to another account. This mostly lines up with XRP Ledger transactions of the `Payment` transaction type, except that the Data API does not consider a transaction to be a payment if the sending `Account` and the `Destination` account are the same, or if the transaction failed.

Payment objects have the following fields:

|Field  |Value  |Description|
|-|-|-|
|amount |String - Number  |The amount of the destination currency that the transaction was instructed to send. In the case of Partial Payments, this is a "maximum" amount.|
|delivered_amount |String - Number  |The amount of the destination currency actually received by the destination account.|
|destination_balance_changes  |Array  |Array of balance change objects, indicating all changes made to the destination account's balances.|
|source_balance_changes |Array  |Array of balance change objects, indicating all changes to the source account's balances (except the XRP transaction cost).|
|transaction_cost |String - Number  |The amount of XRP spent by the source account on the transaction cost.|
|destination_tag  |Integer  |(May be omitted) A destination tag specified in this payment.|
|source_tag |Integer  |(May be omitted) A source tag specified in this payment.|
|currency |String - Currency Code |The currency that the destination account received.|
|destination  |String - Address |The account that received the payment.|
|executed_time  |String - Timestamp |The time the ledger that included this payment closed.|
|ledger_index |Number - Ledger Index  |The sequence number of the ledger that included this payment.|
|source |String - Address |The account that sent the payment.|
|source_currency  |String - Currency Code |The currency that the source account spent.
|tx_hash  |String - Hash  |The identifying hash of the transaction that caused the payment.|

### Balance Objects and Balance Change Objects

Balance objects represent an XRP Ledger account's balance in a specific currency with a specific counterparty at a single point in time. Balance change objects represent a change to such balances that occurs in transaction execution.

A single XRP Ledger transaction may cause changes to balances with several counterparties, as well as changes to XRP.

Balance objects and Balance Change objects have the same format, with the following fields:

|Field  |Value  |Description|
|-|-|-|
|counterparty |String - Address |The counterparty, or issuer, of the `currency`. In the case of XRP, this is an empty string.|
|currency |String - Currency Code |The currency for which this balance changed.|
|value  |String - Number  |The amount of the `currency` that the associated account gained or lost. In balance change objects, this value can be positive (for amounts gained) or negative (for amounts lost). In balance objects, this value can be positive (for amounts the counterparty owes the account) or negative (for amounts owed to the counterparty).

### Balance Change Descriptors

Balance Change Descriptors are objects that describe and analyze a single balance change that occurs in transaction execution. They represent the same events as balance change objects, but in greater detail.

Balance Change Descriptors have the following fields:

|Field  |Value  |Description|
|-|-|-|
|amount_change  |String - Number  |The difference in the amount of currency held before and after this change.|
|final_balance  |String - Number  |The balance after the change occurred.|
|node_index |Number (or null) |This balance change is represented by the entry at this index of the ModifiedNodes array within the metadata section of the transaction that executed this balance change. Note: When the transaction cost is combined with other changes to XRP balance, the transaction cost has a node_index of null instead.|
|tx_index |Number |The transaction that executed this balance change is at this index in the array of transactions for the ledger that included it.|
|change_type  |String |One of several describing what caused this balance change to occur.|
|currency |String - Currency Code |The change affected this currency.|
|executed_time  |String - Timestamp |The time the change occurred. (This is based on the close time of the ledger that included the transaction that executed the change.|
|counterparty |String - Address |(Omitted for XRP) The `currency` is held in a trust line to or from this account. |
|ledger_index |Number - Ledger Index  |The sequence number of the ledger that included the transaction that executed this balance change.|
|tx_hash  |String - Hash  |The identifying hash of the transaction that executed this balance change.|

##### Change Types

The following values are valid for the change_type field of a Balance Change Descriptor:

|Value  |Meaning|
|-|-|
|transaction_cost |This balance change reflects XRP that was destroyed to relay a transaction.|
|payment_destination  |This balance change reflects currency that was received from a payment.|
|payment_source |This balance change reflects currency that was spent in a payment.|
|exchange |This balance change reflects currency that was traded for other currency, or the same currency from a different issuer. This can occur in the middle of payment execution as well as from offers.|

### Volume Objects

Volume objects represent the total volumes of money moved, in either payments or exchanges, during a given period.

|Field  |Value  |Description|
|-|-|-|
|components |Array of Objects |The data that was used to assemble this total. For payment volume, each object represents payments in a particular currency and issuer. For exchange volume, each object represents a market between two currencies.|
|count  |Number |The total number of exchanges in this period.|
|endTime  |String - Timestamp |The end time of this interval.|
|exchange |Object |Indicates the display `currency` used, as with fields currency and (except for XRP) `issuer`. All amounts are normalized by first converting to XRP, and then to the display currency specified in the request.|
|exchangeRate |Number |The exchange rate to the displayed currency from XRP.|
|startTime  |String - Timestamp |The start of this period.|
|total  |Number |Total volume of all recorded exchanges in the period.|

### Server Objects

A "Server Object" describes one rippled server in the XRP Ledger peer-to-peer network. Server objects are returned by the Get Topology, Get Toplogy Nodes, and Get Topology Node methods. The Data API collects reported network topology approximately every 30 seconds using the peer crawler.

Server objects have the following fields, with some only appearing if the request specified a verbose response:

|Field  |Value  |Description|
|-|-|-|
|node_public_key  |String - Base-58 Public Key  |The public key used by this server to sign its peer-to-peer communications, not including validations.|
|version  |String |The `rippled` version of this server, when it was last asked.|
|uptime |Integer  |Number of seconds this server has been connected to the network.|
|ip |String |(May be omitted) IP address of the node (may be omitted)|
|port |Integer  |(May be omitted) Port where this server speaks the `rippled` Peer Protocol.|
|inbound_count  |Integer  |(May be omitted) Number of inbound peer-to-peer connections to this server.|
|inbound_added  |String |(May be omitted) Number of new inbound peer-to-peer connections since the last measurement.|
|inbound_dropped  |String |(May be omitted) Number of inbound peer-to-peer connections dropped since the last measurement.|
|outbound_count |Integer  |(May be omitted) Number of outbound peer-to-peer connections to this server.|
|outbound_added |String |(May be omitted) Number of new outbound peer-to-peer connections since the last measurement.|
|outbound_dropped |String |(May be omitted) Number of outbound peer-to-peer connections dropped since the last measurement.|
|city |String |(Verbose only) The city where this server is located, according to IP geolocation.|
|region |String |(Verbose only) The region where this server is located, according to IP geolocation.|
|country  |String |(Verbose only) The country where this server is located, according to IP geolocation.|
|region_code  |String |(Verbose only) The ISO code for the region where this server is located, according to IP geolocation.|
|country_code |String |(Verbose only) The ISO code for the country where this server is located, according to IP geolocation.|
|postal_code  |String |(Verbose only) The postal code where this server is located, according to IP geolocation.|
|timezone |String |(Verbose only) The ISO timezone where this server is located, according to IP geolocation.|
|lat  |String |(Verbose only) The latitude where this server is located, according to IP geolocation.|
|long |String |(Verbose only) The longitude where this server is located, according to IP geolocation.|
|isp  |String |(Verbose only) The Internet Service Provider hosting this server's public IP address.|
|org  |String |(Verbose only) The organization that owns this server's public IP address.|

### Link Objects

A Link Object represents a peer-to-peer network connection between two rippled servers. It has the following fields:

|Field  |Value  |Description|
|-|-|-|
|source |String - Base-58 Public Key  |The node public key of the rippled making the outgoing connection.|
|target |String - Base-58 Public Key  |The node public key of the rippled receiving the incoming connection.|

### Validation Objects

A Validation Object represents one vote from a validator to mark a ledger version as validated. (A ledger is only validated by the consensus process if a quorum of trusted validators votes for the same exact ledger version.)

*The Data API keeps only about 6 months of validation vote data.*

### A Validation Object has the following fields:

|Field  |Value  |Description|
|-|-|-|
|count  |Integer  |(May be omitted) The number of rippled servers that reported seeing this validation. Not available for old data.|
|ledger_hash  |String - Hash  |The hash of the ledger version this validation vote applies to.|
|reporter_public_key  |String - Base-58 Public Key  |The public key of the rippled server that first reported this validation, in base-58.|
|validation_public_key  |String - Base-58 Public Key  |The public key of the validator used to sign this validation, in base-58.|
|signature  |String |The validator's signature of the validation details, in hexadecimal.|
|first_datetime |String - Timestamp |Date and time of the first report of this validation.|
|last_datetime  |String - Timestamp |Date and time of the last report of this validation.|



## Data API

The Ripple Data API provides access to information about changes in the XRP Ledger, including transaction history and processed analytical data. This information is stored in a dedicated database, which frees rippled servers to keep fewer historical ledger versions.

##### Get Ledger

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

##### Get Ledger Validations

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

##### Get Ledger Validation

Retrieve a validation vote recorded for a specific ledger hash by a specific validator. This dataset includes ledger versions that are outside the validated ledger chain.
`GET /v2/ledgers/{:ledger_hash}/validations/{:pubkey}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|--|--|--|
|ledger_hash	|Hash	|Ledger hash to retrieve validations for.|
|pubkey	|String - Base-58 Public Key	|Validator public key.|

##### Get Transaction

Retrieve a specific transaction by its identifying hash.
`GET /v2/transactions/{:hash}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|--|--|--|
|hash	|String - Hash	|The identifying hash of the transaction.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|--|--|--|
|result	|String	|The value success indicates that this is a successful response.|
|transaction	|Transaction object	|The requested transaction.|

##### Get Transactions

Retrieve transactions by time
`GET /v2/transactions/`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|--|--|--|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|type	|String	|Filter transactions to a specific transaction type.|
|result	|String	|Filter transactions for a specific transaction result.|
|binary	|Boolean	|If true, return transactions in binary form. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 20. Cannot be more than 100.|
|marker	|String	|Pagination marker from a previous response.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|--|--|--|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of Transactions returned.|
|marker	|String	(May be omitted) |Pagination marker.|
|transactions	|Array of Transaction object	|The requested transactions.|

##### Get Payments

Retrieve Payments over time, where Payments are defined as Payment type transactions where the sender of the transaction is not also the destination.
`GET /v2/payments/`
`GET /v2/payments/{:currency}`

This method uses the following URL parameters:

|Field	|Value	|Description|
|--|--|--|
|:currency	|String	(Optional) |Currency code, followed by + and a counterparty address. (Or XRP with no counterparty.) If omitted, return payments for all currencies.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|--|--|--|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|interval	|String	|If provided and currency is also specified, return results aggregated into intervals of the specified length instead of individual payments. Valid intervals are day, week, or month.|
|descending	|Boolean |If true, return results in reverse chronological order. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

##### Get Exchanges

Retrieve Exchanges for a given currency pair over time. Results can be returned as individual exchanges or aggregated to a specific list of intervals
`GET /v2/exchanges/{:base}/{:counter}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|base	|String	|Base currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|
|counter	|String	|Counter currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|interval	|String	|Aggregation interval: 1minute, 5minute, 15minute, 30minute, 1hour, 2hour, 4hour, 1day, 3day, 7day, or 1month. Defaults to non-aggregated results.|
|descending	|Boolean	|If true, return results in reverse chronological order.|
|reduce	|Boolean	|Aggregate all individual results. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 20,000 if reduce is true. Otherwise cannot be more than 1,000.|
|marker	|String	|Pagination key from previously returned response.|
|autobridged	|Boolean	|If true, filter results to autobridged exchanges only.|
|format	|String	|Format of returned results: csv or json. Defaults to json|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of Transactions returned.|
|marker	|String	(May be omitted) |Pagination marker.|
|exchanges	|Array of Exchange Objects	|The requested exchanges.|

##### Get Exchange Rates

Retrieve an exchange rate for a given currency pair at a specific time.
`GET /v2/exchange_rates/{:base}/{:counter}`
This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|base	|String	|Base currency of the pair, as a Currency Code, followed by + and the issuer Address. Omit the + and the issuer for XRP.|
|counter	|String	|Counter currency of the pair, as a Currency Code, followed by + and the issuer Address. Omit the + and the issuer for XRP.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|Return an exchange rate for the specified time. Defaults to the current time.|
|strict	|Boolean	|If false, allow rates derived from less than 10 exchanges. Defaults to true.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|rate	|Number	|The requested exchange rate, or 0 if the exchange rate could not be determined.|

##### Normalize

Convert an amount from one currency and issuer to another, using the network exchange rates
`GET /v2/normalize`

You must provide at least some of the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|amount	|Number	|(Required) Amount of currency to normalize.|
|currency	|String - Currency Code	|The currency code of the amount to convert from. Defaults to XRP.|
|issuer	|String - Address	|The issuer of the currency to convert from. (Required if currency is not XRP.)|
|exchange_currency	|String - Currency Code	|The currency to convert to. Defaults to XRP.|
|exchange_issuer |String - Address |The issuer of the currency to convert to. (Required if exchange_currency is not XRP.)|
|date	|String - Timestamp	|Convert according to the exchange rate at this time. Defaults to the current time.|
|strict	|Boolean	|If true, do not use exchange rates that are determined by less than 10 exchanges. Defaults to true.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|amount	|Number	|Pre-conversion amount specified in the request.|
|converted	|Number	|Post-conversion amount of the exchange_currency, or 0 if the exchange rate could not be determined.|
|rate	|Number	|Exchange rate used to calculate the conversion, or 0 if the exchange rate could not be determined.|

##### Get Daily Reports

Retrieve per account per day aggregated payment summaries
`GET /v2/reports/{:date}`

This method uses the following URL parameter:

|Field	|Value	|Description|
|-|-|-|
|date	|String	|(Optional) UTC query date. If omitted, use the current day.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|accounts	|Boolean	|If true, include lists of counterparty accounts. Defaults to false.|
|payments	|Boolean	|If true, include lists of individual payments. Defaults to false.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|date	|String - Timestamp	|The date for which this report applies.|
|count	|Integer	|Number of reports returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|reports	|Array of Reports Objects	|The requested reports. Each report pertains to a single account.|

##### Get Stats

Retrieve statistics about transaction activity in the XRP Ledger, divided into intervals of time.
`GET /v2/stats`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|family	|String	|If provided, filter results to a single family of stats: type, result, or metric. By default, provides all stats from all families.|
|metrics	|String	|Filter results to one or more metrics (in a comma-separated list). Requires the family of the metrics to be specified. By default, provides all metrics in the family.|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|interval	|String	|Aggregation interval (hour,day,week, defaults to day)|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Families and Metrics
The family and metrics query parameters provide a way to filter results to a specific subset of all metrics available for transactions in any given interval. Each metric is tied to a specific family, as follows:

|Field	|Included Metrics	|Meaning|
|-|-|-|
|type	|All XRP Ledger transaction types, including Payment, AccountSet, OfferCreate, and others.	|Number of transactions of the given type that occurred during the interval.|
|result	|All transaction result codes (string codes, not the numeric codes), including tesSUCCESS, tecPATH_DRY, and many others.	|Number of transactions that resulted in the given code during the interval.|
|metric	|Data-API defined Special Transaction Metrics.	|(Varies)|

Special Transaction Metrics
The Data API derives the following values for every interval. These metrics are part of the metric family.

|Field	|Value	|Description|
|-|-|-|
|accounts_created	|Number	|The number of new accounts funded during this interval.|
|exchanges_count	|Number	|The number of currency exchanges that occurred during this interval.|
|ledger_count	|Number	|The number of ledgers closed during this interval.
|ledger_interval	|Number	|The average number of seconds between ledgers closing during this interval.|
|payments_count	|Number	|The number of payments from one account to another during this interval.|
|tx_per_ledger	|Number	|The average number of transactions per ledger in this interval.|

If any of the metrics have a value of 0, they are omitted from the results.

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of reports returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|stats	|Array of stats objects	|The requested stats. Omits metrics with a value of 0, and intervals that have no nonzero metrics.|

##### Get Capitalization

Get the total amount of a single currency issued by a single issuer, also known as the market capitalization
`GET /v2/capitaliztion/{:currency}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|:currency	|String	|Currency to look up, in the form of currency+issuer. XRP is disallowed.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to 2013-01-01T00:00:00Z.|
|end	|String - Timestamp	|End time of query range. Defaults to the current time.
|interval	|String	|Aggregation interval - day, week, or month. Defaults to day.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.
|marker	|String	|Pagination key from previously returned response.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|adjusted	|Boolean	|If true, do not count known issuer-owned addresses towards market capitalization. Defaults to true.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

If the request omits both start and end, the API returns only the most recent sample.

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of reports returned.|
|currency	|String	|Currency requested.|
|issuer	|String	|Issuer requested.|
|marker	|String	|(May be omitted) Pagination marker.|
|rows	|Array of issuer capitalization objects	|The requested capitalization data.

Each issuer capitalization object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|The start time of the interval this object represents.|
|amount	|String - Number	|The total amount of currency issued by the issuer as of the start of this interval.|

##### Get Active Accounts

Get information on which accounts are actively trading in a specific currency pair.
`GET /v2/active_accounts/{:base}/{:counter}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|:base	|String	|Base currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|
|:counter	|String	|Counter currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|period	|String	|Get results for trading activity during a chosen time period. Valid periods are 1day, 3day, or 7day. Defaults to 1day.|
|date	|String	|Get results for the period starting at this time. Defaults to the most recent period available.|
|include_exchanges	|Boolean	|Include individual exchanges for each account in the results.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of accounts returned.|
|exchanges_count	|Integer	|Total number of exchanges in the period.|
|accounts	|Array of active Account Trading Objects	|Active trading accounts for the period.|

Each "Account Trading Object" describes the activity of a single account during this time period, and has the following fields:

|Field	|Value	|Description|
|-|-|-|
|buy	|Object	|Summary of currency exchanges buying the base currency|
|buy.base_volume	|Number	|Amount of base currency the account bought in this period.|
|buy.counter_volume	|Number	|Amount of counter currency the account sold in this period.|
|buy.count	|Number	|Number of trades that bought the base currency in this period.|
|sell	|Object	|Summary of currency changes selling the base currency.|
|sell.base_volume	|Number	|Amount of the base currency the account sold this period.|
|sell.counter_volume	|Number	|Amount of the counter currency the account bought this period.|
|sell.count	|Number	|Number of trades that sold the base currency.|
|account	|String - Address	|The address whose activity this object describes.|
|base_volume	|Number	|The total volume of the base currency the account bought and sold in this period.|
|counter_volume	|Number	|The total volume of the counter currency the account bought and sold in this period.|
|count	|Number	|The total number of exchanges the account made during this period.|

##### Get Exchange Volume

Get aggregated exchange volume for a given time period. (New in v2.0.4)

The API returns results in units of a single display currency rather than many different currencies. The conversion uses standard rates to and from XRP.
`GET /v2/network/exchange_volume
`Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the start of the most recent interval.|
|end	|String - Timestamp	|End time of query range. Defaults to the end of the most recent interval.|
|interval	|String	|Aggregation interval - valid intervals are day, week, or month. Defaults to day.|
|live	|String	|Return a live rolling window of this length of time. Valid values are day, hour, or minute. Ignored if interval is provided. (New in v2.3.0)|
|exchange_currency	|String - Currency Code	|Normalize all amounts to use this as a display currency. If not XRP, exchange_issuer is also required. Defaults to XRP.|
|exchange_issuer	|String - Address	|Normalize results to the specified currency issued by this issuer.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of results returned.|
|rows	|Array of exchange Volume Objects	|Exchange volumes for each interval in the requested time period. (By default, this array contains only the most recent complete interval. If live is specified and interval isn't, this array contains the specified rolling window instead.)|

Each object in the components array of the Volume Objects represent the volume of exchanges in a market between two currencies, and has the following fields:

|Field	|Value	|Description|
|-|-|-|
|count	|Number	|The number of exchanges in this market during this interval.|
|rate	|Number	|The exchange rate from the base currency to the display currency.|
|amount	|Number	|The amount of volume in the market, in units of the base currency.|
|base	|Object	|The currency and issuer of the base currency of this market. There is no issuer for XRP.|
|counter	|Object	|The currency and issuer of the counter currency of this market. There is no issuer for XRP.|
|converted_amount	|Number	|The total amount of volume in the market, converted to the display currency.|

##### Get Payment Volume

Get aggregated payment volume for a given time period.

The API returns results in units of a single display currency rather than many different currencies. The conversion uses standard rates to and from XRP.

`GET /v2/network/payment_volume`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the start of the most recent interval.|
|end	|String - Timestamp	|End time of query range. Defaults to the end of the most recent interval.|
|interval	|String	|Aggregation interval - valid intervals are day, week, or month. Defaults to day.|
|live	|String	|Return a live rolling window of this length of time. Valid values are day, hour, or minute. Ignored if interval is provided.|
|exchange_currency	|String - Currency Code	|Normalize all amounts to use this as a display currency. If not XRP, exchange_issuer is also required. Defaults to XRP.|
|exchange_issuer	|String - Address	|Normalize results to the specified currency issued by this issuer.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of results returned.|
|rows	|Array of payment Volume Objects	|Payment volumes for each interval in the requested time period. (By default, this array contains only the most recent interval. If live is specified and interval isn't, this array contains the specified rolling window instead.)|

Each object in the components array of the Volume Objects represent the volume of payments for one currencies and issuer, and has the following fields:

|Field	|Value	|Description|
|-|-|-|
|currency	|String - Currency Code	|The currency of this payment volume object.|
|issuer	|String - Address	|(Omitted for XRP) The issuer of this payment volume object.|
|amount	|Number	|Total payment volume for this currency during the interval, in units of the currency itself.|
|count	|Number	|The total number of payments in this currency.|
|rate	|Number	|The exchange rate between this currency and the display currency.|
|converted_amount	|Number	|Total payment volume for this currency, converted to the display currency. |

##### Get Issued Value

Get the total value of all currencies issued by major gateways over time. By default, returns only the most recent measurement.

The API returns results in units of a single display currency rather than many different currencies. The conversion uses standard rates to and from XRP.
`GET /v2/network/issued_value`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the start of the most recent interval.|
|end	|String - Timestamp	|End time of query range. Defaults to the end of the most recent interval.|
|exchange_currency	|String - Currency Code	|Normalize all amounts to use this as a display currency. If not XRP, exchange_issuer is also required. Defaults to XRP.|
|exchange_issuer	|String - Address	|Normalize results to the specified currency issued by this issuer.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of results returned.|
|rows	|Array of Issued Value Objects	|Aggregated capitalization at the requested point(s) in time.|

Each Issued Value Object represents the total value issued at one point in time, and has the following fields:

|Field	|Value	|Description|
|-|-|-|
|components	|Array of Objects	|The data on individual issuers that was used to assemble this total.|
|exchange	|Object	|Indicates the display currency used, as with fields currency and (except for XRP) issuer. All amounts are normalized by first converting to XRP, and then to the display currency specified in the request.|
|exchangeRate	|Number	|The exchange rate to the displayed currency from XRP.|
|time	|String - Timestamp	|When this data was measured.|
|total	|Number	|Total value of all issued assets at this time, in units of the display currency.|

##### Get XRP Distribution

Get information on the total amount of XRP in existence and in circulation, by weekly intervals.

`GET /v2/network/xrp_distribution`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the start of the most recent interval.|
|end	|String - Timestamp	|End time of query range. Defaults to the end of the most recent interval.|
|limit	|Integer |Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|descending	|Boolean |If true, return results in reverse chronological order. Defaults to false.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer|	Number of rows returned.|
|rows	|Array of Distribution Objects	|Weekly snapshots of the XRP distribution.|

Each Distribution Object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|The time of this snapshot.|
|total	|String	|Total XRP in existence.|
|undistributed	|String	|Aggregate amount of XRP held by Ripple (the company).|
|distributed	|String	|Aggregate amount of XRP held by others.|

##### Get Top Currencies

Returns the top currencies on the XRP Ledger, ordered from highest rank to lowest. The ranking is determined by the volume and count of transactions and the number of unique counterparties. By default, returns results for the 30-day rolling window ending on the current date. You can specify a date to get results for the 30-day window ending on that date.
`GET /v2/network/top_currencies`
`GET /v2/network/top_currencies/{:date}`

This method uses the following URL parameter:

|Field	|Value	|Description|
|-|-|-|
|date	|String - ISO 8601 Date	|(Optional) Historical date to query. If omitted, use the most recent date available.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|limit	|Integer |Maximum results per page. Defaults to 1000. Cannot be more than 1000.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|date	|String - Timestamp	|When this data was measured.|
|count	|Integer	|Number of objects in the currencies field.|
|currencies	|Array of Top Currency Objects	|The top currencies for this data sample. Each member represents one currency, by currency code and issuer.|

Each Top Currency Object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|currency |String - Currency Code	|The currency this object describes.|
|issuer	|String - Address |The XRP Ledger address that issues this currency.|
|avg_exchange_count	|String - Number |Daily average number of exchanges|
|avg_exchange_volume |String - Number |Daily average volume of exchanges, normalized to XRP|
|avg_payment_count	|String - Number |Daily average number of payments
|avg_payment_volume	|String - Number |Daily average volume of payments, normalized to XRP|
|issued_value |String - Number |Total amount of this currency issued by this issuer, normalized to XRP|

##### Get Top Markets

Returns the top exchange markets on the XRP Ledger, ordered from highest rank to lowest. The rank is determined by the number and volume of exchanges and the number of counterparties participating. By default, returns top markets for the 30-day rolling window ending on the current date. You can specify a date to get results for the 30-day window ending on that date.
`GET /v2/network/top_markets`
`GET /v2/network/top_markets/{:date}`

This method uses the following URL parameter:

|Field	|Value	|Description|
|-|-|-|
|date	|String - ISO 8601 Date	|(Optional) Historical date to query. If omitted, use the most recent date available.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|limit |Integer |Maximum results per page. Defaults to 1000. Cannot be more than 1000.|
|format	|String |Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|date |String - Timestamp |The end of the rolling window over which this data was calculated.|
|count |Integer	|Number of results in the markets field.|
|markets |Array of Top Market Objects |The top markets for this data sample. Each member represents a currency pair.|

Each Top Market object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|base_currency |String - Currency Code	|The base currency for this market.|
|base_issuer |String - Address |(Omitted if base_currency is XRP) The XRP Ledger address that issues the base currency.|
|counter_currency |String - Currency Code	|The counter currency for this market.|
|counter_issuer	|String - Address	|(Omitted if counter_currency is XRP) The XRP Ledger address that issues the counter currency.|
|avg_base_volume |String |Daily average volume in terms of the base currency.|
|avg_counter_volume	|String	|Daily average volume in terms of the counter currency.|
|avg_exchange_count	|String	|Daily average number of exchanges|
|avg_volume	|String	|Daily average volume, normalized to XRP|

##### Get Transaction Costs

Returns transaction cost stats per ledger, hour, or day. The data shows the average, minimum, maximum, and total transaction costs paid for the given interval or ledger.
`GET /v2/network/fees`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start |String - Timestamp |Start time of query range. Defaults to the earliest data available.|
|end |String - Timestamp |End time of query range. Defaults to the latest data available.|
|interval |String |Aggregation interval - valid intervals are ledger, hour, or day. Defaults to ledger.|
|descending	|Boolean |If true, sort results with most recent first. By default, sort results with oldest first.|
|limit	|Integer |Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|marker	|String	|(May be omitted) Pagination marker.|
|count |Integer |Number of results in the markets field.|
|rows |Array of Fee Summary Objects	|Transaction cost statistics for each interval.|

Each Fee Summary object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|avg |Number |Average transaction cost paid in this interval.|
|min |Number |Minimum transaction cost paid in this interval.|
|max |Number |Maximum transaction cost paid in this interval.|
|total |Number	|Total XRP destroyed by transaction costs.|
|tx_count |Number |Number of transactions in this interval.|
|date |String - Timestamp |The start time of this interval (time intervals), or the close time of this ledger (ledger interval).|
|ledger_index	|Integer - Ledger Index	|(Only present in ledger interval) The ledger this object describes.|

##### Get Topology

Get known rippled servers and peer-to-peer connections between them.
`GET /v2/network/topology`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|Date and time for historical query. By default, uses the most recent data available.|
|verbose |Boolean |If true, include additional details about each server where available. Defaults to false.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|date	|String - Timestamp	|The time of this measurement.|
|node_count	|Integer |Number of rippled servers in the topology.|
|link_count	|Integer |Number of links in the topology.|
|nodes |Array of Server Objects |Details of rippled servers in the peer-to-peer network.|
|links |Array of Link Objects |Network connections between rippled servers in the peer-to-peer network.|

##### Get Topology Nodes

Get known rippled nodes. (This is a subset of the data returned by the Get Topology method.)
`GET /v2/network/topology/nodes`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|date |String - Timestamp |Date and time for historical query. Defaults to most recent data.|
|verbose |Boolean |If true, return full details for each server. Defaults to false.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String |The value success indicates that the body represents a successful response.|
|date |String - Timestamp	|When this the data was measured.|
|count |Integer	|Number of rippled servers described.|
|nodes |Array of Server Objects	|Details of the rippled servers in the topology.|

##### Get Topology Node

Get information about a single rippled server by its node public key (not validator public key).
`GET /v2/network/topology/nodes/{:pubkey}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|pubkey	|String - Base-58 Public Key|Node public key of the server to look up.|

This method takes no query parameters.

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with a Server Object in the response with the following additional field:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|

##### Get Topology Links

Get information on peer-to-peer connections between rippled servers. (This is a subset of the data returned by the Get Topology method.)
`GET /v2/network/topology/links`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|Date and time for historical query. Defaults to most recent data available.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|date	|String - Timestamp	|When this data was measured.|
|count	|Integer	|Number of links returned.|
|links	|Array of Link Objects	|Links between rippled servers.|

##### Get Validator

Get details of a single validator in the consensus network.
`GET /v2/network/validators/{:pubkey}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|pubkey	|String - Base-58 Public Key	|Validator public key.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|last_datetime	|Integer	|The last reported validation vote signed by this validator.|
|validation_public_key	|String - Base-58 Public Key |This validator's validator public key.|
|domain	|String	|(May be omitted) The DNS domain associated with this validator.|
|domain_state	|String	|The value verified indicates that this validator has a verified domain controlled by the same operator as the validator. The value AccountDomainNotFound indicates that the "Account Domain" part of Domain Verification is not set up properly. The value RippleTxtNotFound indicates that the ripple.txt step of Domain Verification is not set up properly.|

##### Get Validators

Get a list of known validators.
`GET /v2/network/validators`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|last_datetime	|Integer |Number of links returned.|
|validation_public_key	|String - Base-58 Public Key |Validator public key of this validator.|

##### Get Validator Validations

Retrieve validation votes signed by a specified validator, including votes for ledger versions that are outside the main ledger chain. (New in v2.2.0)

*The Data API does not have a comprehensive record of all validations. The response only includes data that the Data API has recorded. Some ledger versions, especially older ledgers, may have no validations even if they were validated by consensus.*

`GET /v2/network/validators/{:pubkey}/validations`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|pubkey	|String - Base-58 Public Key |Validator public key.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|limit	|Integer |Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer |Number of validations returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|validations	|Array of Validation Objects	|The requested validations.|

##### Get Validations

Retrieve validation votes, including votes for ledger versions that are outside the main ledger chain.

*The Data API does not have a comprehensive record of all validations. The response only includes data that the Data API has recorded. Some ledger versions, especially older ledgers, may have no validations even if they were validated by consensus.*

`GET /v2/network/validations`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|limit	|Integer |Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|
|descending	|Boolean |If true, return results sorted with earliest first. Otherwise, return oldest results first. Defaults to false.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer	|Number of validation votes returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|validations	|Array of Validation Objects |The requested validation votes.|

##### Get Single Validator Reports

Get a single validator's validation vote stats for 24-hour intervals.

`GET /v2/network/validators/{:pubkey}/reports`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|pubkey	|String	|Validator public key.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start date and time for historical query. Defaults to 200 days before the current date.|
|end	|String - Timestamp	|End date and time for historical query. Defaults to most recent data available.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer |Number of validators returned.|
|validators	|Array of Single Validator Report Objects	|Daily reports of this validator's validation votes.|

Each member in the validators array is a Single Validator Report Object with data on that validator's performance on that day. Each has the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|The start time of the date this object describes.|
|total_ledgers	|Integer	|Number of ledger hashes for which this validator submitted validation votes. If this number is much lower than other validators in the same time period, that could mean the validator had downtime.|
|main_net_agreement	|String - Number	|The fraction of consensus-validated production network ledger versions for which this validator voted in this interval. "1.0" indicates 100% agreement.|
|main_net_ledgers	|Integer	|Number of consensus-validated production network ledger versions this validator voted for.|
|alt_net_agreement	|String - Number	|The fraction of the consensus-validated Test Network ledger versions this validator voted for. "1.0" indicates 100% agreement.|
|alt_net_ledgers |Integer	|Number of consensus-validated Test Network ledger versions this validator voted for.|
|other_ledgers	|Integer |Number of other ledger versions this validator voted for. If this number is high, that could indicate that this validator was running non-standard or out-of-date software.|

##### Get Daily Validator Reports

Get a validation vote stats and validator information for all known validators in a 24-hour period.

`GET /v2/network/validator_reports`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|Date and time to query. By default, uses the most recent data available.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

Response Format
A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer	|Number of reports returned.|
|reports |Array of Daily Validator Report Objects |Summaries of activity for each validator active during this time period.|

Daily Validator Report Object fields:

|Field	|Value	|Description|
|-|-|-|
|validation_public_key	|String - Base-58 Public Key	|This validator's validator public key.|
|date	|String - Timestamp	|The start time of the date this object describes.|
|total_ledgers	|Integer	|Number of ledger indexes for which this validator submitted validation votes. If this number is much lower than other validators in the same time period, that could mean the validator had downtime.|
|main_net_agreement	|String - Number	|The fraction of consensus-validated production network ledger versions for which this validator voted in this interval. "1.0" indicates 100% agreement.|
|main_net_ledgers	|Integer	|Number of consensus-validated production network ledger versions this validator voted for.|
|alt_net_agreement	|String - Number	|The fraction of the consensus-validated Test Network ledger versions this validator voted for. "1.0" indicates 100% agreement.|
|alt_net_ledgers	|Integer	|Number of consensus-validated Test Network ledger versions this validator voted for.|
|other_ledgers	|Integer	|Number of other ledger versions this validator voted for. If this number is high, that could indicate that this validator was running non-standard or out-of-date software.|
|last_datetime	|Integer |The last reported validation vote signed by this validator.|
|domain	|String	|(May be omitted) The DNS domain associated with this validator.|
|domain_state	|String	|The value verified indicates that this validator has a verified domain controlled by the same operator as the validator. The value AccountDomainNotFound indicates that the "Account Domain" part of Domain Verification is not set up properly. The value RippleTxtNotFound indicates that the ripple.txt step of Domain Verification is not set up properly.|

##### Get rippled Versions

Reports the latest versions of rippled available from the official Ripple Yum repositories.
`GET /v2/network/rippled_versions`

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that the body represents a successful response.|
|count	|Integer	|Number of rows returned.|
|rows	|Array of Version Objects	|Description of the latest rippled version in each repository.|

Each Version Object contains the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|The date this rippled version was released.|
|repo	|String	|The Yum repository where this rippled is available. The stable repository has the latest production version. Other versions are for development and testing.|
|version	|String	|The version string for this version of rippled.|

#### Get All Gateways

Get information about known gateways.
`GET /v2/gateways/`

A successful response uses the HTTP code 200 OK and has a JSON body.

Each field in the top level JSON object is a Currency Code. The content of each field is an array of objects, representing gateways that issue that currency. Each object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|name	|String	|A human-readable proper name for the gateway.|
|account	|String - Address	|The issuing address of this currency.|
|featured	|Boolean	|Whether this gateway is considered a "featured" issuer of the currency. Ripple decides which gateways to feature based on responsible business practices, volume, and other measures.|
|label	|String	|(May be omitted) Only provided when the Currency Code is a 40-character hexadecimal value. This is an alternate human-readable name for the currency issued by this gateway.|
|assets	|Array of Strings	|Graphics filenames available for this gateway, if any. (Mostly, these are logos used by XRP Charts.)|

##### Get Gateway

Get information about a specific gateway from the Data API's list of known gateways.
`GET /v2/gateways/{:gateway}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|gateway	|String	|The issuing Address, URL-encoded name, or normalized name of the gateway.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|name	|String	|Human-readable name of the gateway.|
|start_date	|String - Timestamp	|The approximate date of the first time exchanges for this gateway's currencies appeared in the ledger.|
|accounts	|Array	|A list of issuing addresses used by this gateway. (Gateways may use different issuing accounts for different currencies.)|
|hotwallets	|Array of Addresses	|This gateway's operational addresses.|
|domain	|String	|The domain name where this gateway does business. Typically the gateway hosts a ripple.txt there.|
|normalized	|String	|A normalized version of the name field suitable for including in URLs.
|assets	|Array of Strings	|Graphics filenames available for this gateway, if any. (Mostly, these are logos used by XRP Charts.)|

Each object in the accounts field array has the following fields:

Field	Value	Description
address	String	The issuing address used by this gateway.
currencies	Object	Each field in this object is a Currency Code corresponding to a currency issued from this address. Each value is an object with a featured boolean indicating whether that currency is featured. Ripple decides which currencies and gateways to feature based on responsible business practices, volume, and other measures.


##### Get Currency Image

Retrieve vector icons for various currencies.
`GET /v2/currencies/{:currencyimage}`

This method requires the following URL parameter:

|Field	|Value	|Description|
|currencyimage	|String	|An image file for a currency, such as xrp.svg. See the source code for a list of available images.|

##### Get Accounts

Retrieve information about the creation of new accounts in the XRP Ledger.
`GET /v2/accounts`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range.|
|end	|String - Timestamp	|End time of query range.|
|interval	|String	|Aggregation interval (hour,day,week). If omitted, return individual accounts. Not compatible with the parent parameter.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1,000.|
|marker	|String	|Pagination key from previously returned response.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|parent	|String	|Filter results to children of the specified parent account. Not compatible with the interval parameter.|
|reduce	|Boolean	|Return a count of results only.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of accounts returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|accounts	|Array	|If the request used the interval query parameter, each member of the array is an interval object. Otherwise, this field is an array of account creation objects.|

If the request uses the interval query parameter, the response has an array of interval objects, each of which represents the number of accounts created during a single interval. Interval objects have the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|When this interval starts. (The length of the interval is determined by the request.)|
|count	|Number	|How many accounts were created in this interval.|

##### Get Account

Get creation info for a specific ripple account
`GET /v2/accounts/{:address}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|account	|Object - Account Creation	|The requested account.|

##### Get Account Balances

Get all balances held or owed by a specific XRP Ledger account.

`GET /v2/accounts/{:address}/balances`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|ledger_index	|Integer	|Index of ledger for historical balances.|
|ledger_hash	|String	Ledger hash for historical balances.|
|date	|String	|UTC date for historical balances.|
|currency	|String	|Restrict results to specified currency.|
|counterparty	|String|	Restrict results to specified counterparty/issuer.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be greater than 400, but you can use the value all to return all results. (Caution: When using limit=all to retrieve very many results, the request may time out. For large issuers, there can be several tens of thousands of results.)|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|ledger_index	|Integer	|Ledger index for balances query.|
|close_time	|String	|Close time of the ledger.|
|limit	|String	|Number of results returned, if limit was exceeded.|
|marker	|String	|(May be omitted) Pagination marker.|
|balances	|Array of Balance Objects	|The requested balances.|

##### Get Account Orders

Get orders in the order books, placed by a specific account. This does not return orders that have already been filled.
`GET /v2/account/{:address}/orders`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String - Address	|XRP Ledger address to query.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|ledger_index	|Integer	|Get orders as of this ledger. Not compatible with ledger_hash or date.|
|ledger_hash	|String	|Get orders as of this ledger. Not compatible with ledger_index or date.|
|date	|String - Timestamp	|Get orders at this time. Not compatible with ledger_index or ledger_hash.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be greater than 400.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

If none of ledger_index, ledger_hash, or date are specified, the API uses the most current data available.

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|ledger_index	|Integer	|ledger_index of the ledger version used.|
|close_time	|String	|Close time of the ledger version used.|
|limit	|String	|The limit from the request.|
|orders	|Array of order objects	|The requested orders.|

Each order object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|specification	|Object	|Details of this order's current state.|
|specification.direction	|String	|Either buy or sell.|
|specification.quantity	|Balance Object	|The maximum amount of the base currency this order would buy or sell (depending on the direction). This value decreases as the order gets partially filled.|
|specification.totalPrice	|Balance Object	|The maximum amount of the counter currency the order can spend or gain to buy or sell the base currency. This value decreases as the order gets partially filled.|
|properties	|Object	|Details of how the order was placed.|
|properties.maker	|String - Address	|The XRP Ledger account that placed the order.|
|properties.sequence	|Number	|The sequence number of the transaction that placed this order.|
|properties.makerExchangeRate	|String - Number	|The exchange rate from the point of view of the account that submitted the order.|

##### Get Account Transaction History

Retrieve a history of transactions that affected a specific account. This includes all transactions the account sent, payments the account received, and payments that rippled through the account.
`GET /v2/accounts/{:address}/transactions`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|:address	|String - Address	|XRP Ledger address to query.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the earliest date available.|
|end	|String - Timestamp	|End time of query range. Defaults to the current date.|
|min_sequence	|String	|Minimum sequence number to query.|
|max_sequence	|String	|Max sequence number to query.|
|type	|String	|Restrict results to a specified transaction type|
|result	|String	|Restrict results to specified transaction result.|
|binary	|Boolean	|Return results in binary format.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 20. Cannot be more than 1,000.|
|marker	|String	|Pagination key from previously returned response.|

*This method cannot return CSV format; only JSON results are supported for raw XRP Ledger transactions.*

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|The number of objects contained in the transactions field.|
|marker	|String	|(May be omitted) Pagination marker.|
|transactions	|Array of transaction objects	|All transactions matching the request.|

##### Get Transaction By Account And Sequence

Retrieve a specifc transaction originating from a specified account

`GET /v2/accounts/{:address}/transactions/{:sequence}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|
|sequence	|Integer	|Transaction sequence number.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|binary	|Boolean	|If true, return transaction in binary format. Defaults to false.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|transaction	|transaction object	|The requested transaction.|

##### Get Account Payments

Retrieve a payments for a specified account

`GET /v2/accounts/{:address}/payments`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Filter results to this time and later.|
|end	|String - Timestamp	|Filter results to this time and earlier.|
|type	|String	|Type of payment - sent or received.|
|currency	|String - Currency Code	|Filter results to specified currency.|
|issuer	|String - Address	|Filter results to specified issuer.|
|source_tag	|Integer	|Filter results to specified source tag.|
|destination_tag	|Integer	|Filter results to specified destination tag.|
|descending	|Boolean	|If true, sort results with most recent first. Otherwise, return oldest results first. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1,000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|The number of objects contained in the payments field.|
|marker	|String	|(May be omitted) Pagination marker.|
|payments	|Array of payment objects	|All payments matching the request.|

##### Get Account Exchanges

Retrieve Exchanges for a given account over time.
`GET /v2/accounts/{:address}/exchanges/`
`GET /v2/accounts/{:address}/exchanges/{:base}/{:counter}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.
|base	|String	|Base currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|
|counter	|String	|Counter currency of the pair, as a Currency Code, followed by + and the issuer Address unless it's XRP.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Filter results to this time and later.
|end	|String - Timestamp	|Filter results to this time and earlier.
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of exchanges returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|exchanges	|Array of Exchange Objects	|The requested exchanges.|

##### Get Account Balance Changes

Retrieve Balance changes for a given account over time.
`GET /v2/accounts/{:address}/balance_changes/`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|

|Field	|Value	|Description|
|-|-|-|
|currency	|String	|Restrict results to specified currency.|
|counterparty	|String	|Restrict results to specified counterparty/issuer.|
|start	|String - Timestamp	|Start time of query range.|
|end	|String - Timestamp	|End time of query range.|
|descending	|Boolean	|If true, return results in reverse chronological order. Defaults to false.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv orjson. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of balance changes returned.|
|marker	|String	|(May be omitted) Pagination marker.|
|exchanges	|Array of balance change descriptors	|The requested balance changes.|

##### Get Account Reports

Retrieve daily summaries of payment activity for an account.
`GET /v2/accounts/{:address}/reports/`
`GET /v2/accounts/{:address}/reports/{:date}`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|
|date	|String	(Optional) |UTC date for single report. If omitted, use the start and end query parameters.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to start of current date. Ignored if date specified.|
|end	|String - Timestamp	|End time of query range. Defaults to current date. Ignored if date specified.|
|accounts	|Boolean	|If true, provide lists with addresses of all sending_counterparties and receiving_counterparties in results. Otherwise, return only the number of sending and receiving counterparties.|
|payments	|Boolean	|Include Payment Summary Objects in the payments field for each interval, with the payments that occurred during that interval.|
|descending	|Boolean	|If true, sort results with most recent first. By default, sort results with oldest first.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of reports in the reports field.|
|reports	|Array of Reports Objects	|Daily summaries of account activity for the given account and date range.|

##### Get Account Transaction Stats

Retrieve daily summaries of transaction activity for an account.
`GET /v2/accounts/{:address}/stats/transactions`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
|address	|String	|XRP Ledger address to query.|

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the earliest date available.|
|end	|String - Timestamp	|End time of query range. Defaults to the current date.|
|limit	|Integer	|Maximum results per page. Defaults to 200. Cannot be more than 1000.|
|descending	|Boolean	|If true, sort results with most recent first. By default, sort results with oldest first.|
|marker	|String	|Pagination key from previously returned response.|
|format	|String	|Format of returned results: csv or json. Defaults to json.|

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.|
|count	|Integer	|Number of transaction stats objects in the rows field.|
|rows	|Array of Transaction Stats Objects	|Daily summaries of account transaction activity for the given account.|

Each Transaction Stats Object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|This object describes activity on this date.|
|transaction_count	|Integer	|The total number of transactions sent by the account on this date.|
|result	|Object	|Map of transaction result codes, indicating how many of each result code occurred in the transactions sent by this account on this date.|
|type	|Object	|Map of transaction types, indicating how many of each transaction type the account sent on this date.|

##### Get Account Value Stats

Retrieve daily summaries of transaction activity for an account.
`GET /v2/accounts/{:address}/stats/value`

This method requires the following URL parameters:

|Field	|Value	|Description|
|-|-|-|
address	String	XRP Ledger address to query.

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|start	|String - Timestamp	|Start time of query range. Defaults to the start of the most recent interval.|
|end	|String - Timestamp	|End time of query range. Defaults to the end of the most recent interval.|
|limit	|Integer	Maximum results per page. Defaults to 200. Cannot be more than 1000.
|marker	|String	|Pagination key from previously returned response.
|descending	|Boolean |If true, sort results with most recent first. By default, sort results with oldest first.
|format	|String	|Format of returned results: csv or json. Defaults to json.

A successful response uses the HTTP code 200 OK and has a JSON body with the following:

|Field	|Value	|Description|
|-|-|-|
|result	|String	|The value success indicates that this is a successful response.
|count	|Integer |Number of value stats objects in the rows field.
|rows	|Array of Value Stats Objects |Daily summaries of account value for the given account.|

Each Value Stats Object has the following fields:

|Field	|Value	|Description|
|-|-|-|
|date	|String - Timestamp	|This object describes activity on this date.|
|value	|String - Number	|The total of all currency held by this account, normalized to XRP.|
|balance_change_count	|Number	|The number of times the account's balance changed on this date.|

##### Health Check - API

Check the health of the API service.
`GET /v2/health/api`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|threshold	|Integer	|Consider the API unhealthy if the database does not respond within this amount of time, in seconds. Defaults to 5 seconds.|
|verbose	|Boolean	|If true, return a JSON response with data points. By default, return an integer value only.|

A successful response uses the HTTP code 200 OK. By default, the response body is an integer health value only.

The health value 0 always indicates a healthy status. Other health values are defined as follows:

|Value	|Meaning|
|-|-|
|0	|API service is up, and response time to HBase is less than threshold value from request.|
|1	|API service is up, but response time to HBase is greater than threshold value from request.|

If the request specifies verbose=true in the query parameters, the response body is a JSON object, with the following fields:

|Field	|Value	|Description|
|-|-|-|
|score	|0-1	|Health value, as defined above.|
|response_time	|String - Human-readable time	|The actual response time of the database.|
|response_time_threshold	|String - Human-readable time	|The maximum response time to be considered healthy.|

##### Health Check - Ledger Importer

Check the health of the Ledger Importer Service.
`GET /v2/health/importer`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|threshold	|Integer	|Consider the Importer unhealthy if more than this amount of time, in seconds, has elapsed since the latest validated ledger was imported. Defaults to 300 seconds.|
|threshold2	|Integer	|Consider the Importer unhealthy if more than this amount of time, in seconds, has elapsed since the latest ledger of any kind was imported. Defaults to 60 seconds.|
|verbose	|Boolean	|If true, return a JSON response with data points. By default, return an integer value only.|

A successful response uses the HTTP code 200 OK. By default, the response body is an integer health value only.

The health value 0 always indicates a healthy status. Other health values are defined as follows:

|Value	|Meaning|
|-|-|
|0	|The most recent imported ledger was less than threshold2 (Default: 60) seconds ago, and most recent validated ledger was less than threshold seconds ago.|
|1	|The most recent imported ledger was less than threshold2 (Default: 60) seconds ago, but the most recent validated ledger is older than threshold seconds.|
|2	|The most recent imported ledger was more than threshold2 seconds ago.

If the request specifies verbose=true in the query parameters, the response body is a JSON object, with the following fields:

|Field	|Value	|Description|
|-|-|-|
|score	|0-2	|Health value, as defined above.|
|response_time	|String	|The actual response time of the database.|
|ledger_gap	|String - Human-readable time	|Difference between the close time of the last saved ledger and the current time.|
|ledger_gap_threshold	|String - Human-readable time	|Maximum ledger gap to be considered healthy.|
|valildation_gap	|String - Human-readable time	|Difference between the close time of the last imported validated ledger and the current time.|
|validation_gap_threshold	|String - Human-readable time	|Maximum validation gap to be considered healthy.|

##### Health Check - Nodes ETL

Check the health of the Topology Nodes Extract, Transform, Load (ETL) Service.

`GET /v2/health/nodes_etl`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|threshold	|Integer	|Consider the service unhealthy if more than this amount of time, in seconds, has elapsed since the latest data was imported. Defaults to 120 seconds.|
|verbose	|Boolean	|If true, return a JSON response with data points. By default, return an integer value only.|

A successful response uses the HTTP code 200 OK. By default, the response body is an integer health value only.

The health value 0 always indicates a healthy status. Other health values are defined as follows:

|Value	|Meaning|
|-|-|
|0	|The most recent imported topology data was less than threshold (Default: 120) seconds ago.|
|1	|The most recent imported topology data was more than threshold seconds ago.|

If the request specifies verbose=true in the query parameters, the response body is a JSON object, with the following fields:

|Field	|Value	|Description|
|-|-|-|
|score	|0-1	|Health value, as defined above.|
|gap	|String - Human-readable time	|Difference between the latest imported data and the current time.|
|gap_threshold	|String - Human-readable time	|Maximum gap to be considered healthy.|
|message	|String	|Description of the reason for a non-zero score, if applicable.|

##### Health Check - Validations ETL

Check the health of the Validations Extract, Transform, Load (ETL) Service.
`GET /v2/health/validations_etl`

Optionally, you can provide the following query parameters:

|Field	|Value	|Description|
|-|-|-|
|threshold	|Integer |Consider the service unhealthy if more than this amount of time, in seconds, has elapsed since the latest data was imported. Defaults to 120 seconds.|
|verbose	|Boolean	|If true, return a JSON response with data points. By default, return an integer value only.|

A successful response uses the HTTP code 200 OK. By default, the response body is an integer health value only.

The health value 0 always indicates a healthy status. Other health values are defined as follows:

|Value	|Meaning|
|-|-|-|
|0	|The most recent imported topology data was less than threshold (Default: 120) seconds ago.|
|1	|The most recent imported topology data was more than threshold seconds ago.|

If the request specifies verbose=true in the query parameters, the response body is a JSON object, with the following fields:

|Field	|Value	|Description|
|-|-|-|
|score	|0-1 |Health value, as defined above.|
|gap	|String - Human-readable time	|Difference between the latest imported data and the current time.|
|gap_threshold	|String - Human-readable time	|Maximum gap to be considered healthy.
message	String	Description of the reason for a non-zero score, if applicable.|

## How to use Drain
1. Config contants at LedgerRipple.py and ElasticRipple.py
1. Start DrainRipple.py from cmd