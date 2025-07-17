## Code Reference

## OpenApiException

Bases: `[Exception](https://docs.python.org/3/library/exceptions.html#Exception)`

OpenAPI exception

### code instance-attribute

```python
code: Optional[int]
```

Error code

### message instance-attribute

```python
message: str
```

Error message

### \_\_init\_\_

```python
__init__(code: int, message: str) -> None
```

## HttpClient

A HTTP client for longPort open api

| Parameters: | - **`http_url`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	HTTP API url - **`app_key`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	App Key - **`app_secret`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	App Secret - **`access_token`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Access Token |
| --- | --- |

### \_\_init\_\_

```python
__init__(http_url: str, app_key: str, app_secret: str, access_token: str) -> None
```

### from\_env classmethod

```python
from_env() -> HttpClient
```

Create a new `HttpClient` from the given environment variables

It first gets the environment variables from the `.env` file in the current directory.

#### Variables

- `LONGPORT_HTTP_URL` - HTTP endpoint url
- `LONGPORT_APP_KEY` - App key
- `LONGPORT_APP_SECRET` - App secret
- `LONGPORT_ACCESS_TOKEN` - Access token

### request

```python
request(method: str, path: str, headers: Optional[dict[str, str]] = None, body: Optional[Any] = None) -> Any
```

Performs a HTTP reqest

Examples:

::

```python
from longport.openapi import HttpClient

client = HttpClient(http_url, app_key,
                    app_secret, access_token);

# get
resp = client.request("get", "/foo/bar");
print(resp)

# post
client.request("get", "/foo/bar", { "foo": 1, "bar": 2 });
```

## PushCandlestickMode

Push candlestick mode

### Realtime

Bases:

Real-time

### Confirmed

Bases:

Confirmed

## Config

Configuration options for LongPort sdk

| Parameters: | - **`app_key`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	App Key - **`app_secret`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	App Secret - **`access_token`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Access Token - **`http_url`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	HTTP API url - **`quote_ws_url`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Websocket url for quote API - **`trade_ws_url`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Websocket url for trade API - **`language`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Language identifier - **`enable_overnight`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`, default: `False`) – 	Enable overnight quote - **`push_candlestick_mode`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`, default: ) – 	Push candlestick mode - **`enable_print_quote_packages`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`, default: `True`) – 	Enable printing the opened quote packages when connected to the server - **`log_path`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Set the path of the log files |
| --- | --- |

### \_\_init\_\_

```python
__init__(app_key: str, app_secret: str, access_token: str, http_url: Optional[str] = None, quote_ws_url: Optional[str] = None, trade_ws_url: Optional[str] = None, language: Optional[Type[Language]] = None, enable_overnight: bool = False, push_candlestick_mode: Type[PushCandlestickMode] = PushCandlestickMode.Realtime, enable_print_quote_packages: bool = True, log_path: Optional[str] = None) -> None
```

### from\_env classmethod

```python
from_env() -> Config
```

Create a new `Config` from the given environment variables

It first gets the environment variables from the `.env` file in the current directory.

#### Variables

- `LONGPORT_LANGUAGE` - Language identifier, `zh-CN`, `zh-HK` or `en` (Default: `en`)
- `LONGPORT_APP_KEY` - App key
- `LONGPORT_APP_SECRET` - App secret
- `LONGPORT_ACCESS_TOKEN` - Access token
- `LONGPORT_HTTP_URL` - HTTP endpoint url
- `LONGPORT_QUOTE_WS_URL` - Quote websocket endpoint url
- `LONGPORT_TRADE_WS_URL` - Trade websocket endpoint url
- `LONGPORT_ENABLE_OVERNIGHT` - Enable overnight quote, `true` or `false` (Default: `false`)
- `LONGPORT_PUSH_CANDLESTICK_MODE` - `realtime` or `confirmed` (Default: `realtime`)
- `LONGPORT_PRINT_QUOTE_PACKAGES` - Print quote packages when connected, `true` or `false` (Default: `true`)
- `LONGPORT_LOG_PATH` - Set the path of the log files (Default: `no logs`)

### refresh\_access\_token

```python
refresh_access_token(expired_at: Optional[datetime] = None) -> str
```

Gets a new `access_token`

| Parameters: | - **`expired_at`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	The expiration time of the access token, defaults to `90` days. |
| --- | --- |

| Returns: | - `[str](https://docs.python.org/3/library/stdtypes.html#str)` – 	Access token |
| --- | --- |

## Language

Language identifier

### ZH\_CN

Bases:

zh-CN

### ZH\_HK

Bases:

zh-HK

### EN

Bases:

en

## Market

Market

### Unknown

Bases:

Unknown

### US

Bases:

US market

### HK

Bases:

HK market

### CN

Bases:

CN market

### SG

Bases:

SG market

## PushQuote

Quote message

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### open instance-attribute

```python
open: Decimal
```

Open

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### trade\_status instance-attribute

```python
trade_status: Type[TradeStatus]
```

Security trading status

### trade\_session instance-attribute

```python
trade_session: Type[TradeSession]
```

Trade session

### current\_volume instance-attribute

```python
current_volume: int
```

Increase volume between pushes

### current\_turnover instance-attribute

```python
current_turnover: Decimal
```

Increase turnover between pushes

## PushDepth

Depth message

### asks instance-attribute

```python
asks: List[Depth]
```

Ask depth

### bids instance-attribute

```python
bids: List[Depth]
```

Bid depth

## PushBrokers

Brokers message

### ask\_brokers instance-attribute

```python
ask_brokers: List[Brokers]
```

Ask brokers

### bid\_brokers instance-attribute

```python
bid_brokers: List[Brokers]
```

Bid brokers

## PushTrades

Trades message

### trades instance-attribute

```python
trades: List[Trade]
```

Trades data

## PushCandlestick

Candlestick updated event

### period instance-attribute

```python
period: Period
```

Period type

### candlestick instance-attribute

```python
candlestick: Candlestick
```

Candlestick

### is\_confirmed instance-attribute

```python
is_confirmed: bool
```

Is confirmed

## SubType

Subscription flags

### Quote

Bases:

Quote

### Depth

Bases:

Depth

### Brokers

Bases:

Broker

### Trade

Bases:

Trade

## DerivativeType

Derivative type

### Option

Bases:

US stock options

### Warrant

Bases:

HK warrants

## SecurityBoard

Security board

### Unknown

Bases:

Unknown

### USMain

Bases:

US Pink Board

### USPink

Bases:

US Pink Board

### USDJI

Bases:

Dow Jones Industrial Average

### USNSDQ

Bases:

Nasdsaq Index

### USSector

Bases:

US Industry Board

### USOption

Bases:

US Option

### USOptionS

Bases:

US Sepecial Option

### HKEquity

Bases:

Hong Kong Equity Securities

### HKPreIPO

Bases:

HK PreIPO Security

### HKWarrant

Bases:

HK Warrant

### HKHS

Bases:

Hang Seng Index

### HKSector

Bases:

HK Industry Board

### SHMainConnect

Bases:

SH Main Board(Connect)

### SHMainNonConnect

Bases:

SH Main Board(Non Connect)

### SHSTAR

Bases:

SH Science and Technology Innovation Board

### CNIX

Bases:

CN Index

### CNSector

Bases:

CN Industry Board

### SZMainConnect

Bases:

SZ Main Board(Connect)

### SZMainNonConnect

Bases:

SZ Main Board(Non Connect)

### SZGEMConnect

Bases:

SZ Gem Board(Connect)

### SZGEMNonConnect

Bases:

SZ Gem Board(Non Connect)

### SGMain

Bases:

SG Main Board

### STI

Bases:

Singapore Straits Index

### SGSector

Bases:

SG Industry Board

## Security

Security

### symbol instance-attribute

```python
symbol: str
```

Security code

### name\_cn instance-attribute

```python
name_cn: str
```

Security name (zh-CN)

### name\_en instance-attribute

```python
name_en: str
```

Security name (en)

### name\_hk instance-attribute

```python
name_hk: str
```

Security name (zh-HK)

## SecurityListCategory

Security list category

### Overnight

Bases:

Overnight

## SecurityStaticInfo

The basic information of securities

### symbol instance-attribute

```python
symbol: str
```

Security code

### name\_cn instance-attribute

```python
name_cn: str
```

Security name (zh-CN)

### name\_en instance-attribute

```python
name_en: str
```

Security name (en)

### name\_hk instance-attribute

```python
name_hk: str
```

Security name (zh-HK)

### exchange instance-attribute

```python
exchange: str
```

Exchange which the security belongs to

### currency instance-attribute

```python
currency: str
```

Trading currency

### lot\_size instance-attribute

```python
lot_size: int
```

Lot size

### dividend\_yield instance-attribute

```python
dividend_yield: Decimal
```

Dividend yield

### stock\_derivatives instance-attribute

```python
stock_derivatives: List[Type[DerivativeType]]
```

Types of supported derivatives

### board instance-attribute

```python
board: Type[SecurityBoard]
```

Board

## TradeStatus

Security Status

### Normal

Bases:

Normal

### Halted

Bases:

Suspension

### Delisted

Bases:

Delisted

### Fuse

Bases:

Fuse

### PrepareList

Bases:

Prepare List

### CodeMoved

Bases:

Code Moved

### ToBeOpened

Bases:

To Be Opened

### SplitStockHalts

Bases:

Split Stock Halts

### Expired

Bases:

Expired

### WarrantPrepareList

Bases:

Warrant To BeListed

### Suspend

Bases:

Suspend

## PrePostQuote

Quote of US pre/post market

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### prev\_close instance-attribute

```python
prev_close: Decimal
```

Close of the last trade session

## SecurityQuote

Quote of securitity

### symbol instance-attribute

```python
symbol: str
```

Security code

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### prev\_close instance-attribute

```python
prev_close: Decimal
```

Yesterday's close

### open instance-attribute

```python
open: Decimal
```

Open

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### trade\_status instance-attribute

```python
trade_status: Type[TradeStatus]
```

Security trading status

### pre\_market\_quote instance-attribute

```python
pre_market_quote: Optional[PrePostQuote]
```

Quote of US pre market

### post\_market\_quote instance-attribute

```python
post_market_quote: Optional[PrePostQuote]
```

Quote of US post market

### overnight\_quote instance-attribute

```python
overnight_quote: Optional[PrePostQuote]
```

Quote of US overnight market

## OptionType

Option type

### Unknown

Bases:

Unknown

### American

Bases:

American

### Europe

Bases:

Europe

## OptionDirection

Option direction

### Unknown

Bases:

Unknown

### Put

Bases:

Put

### Call

Bases:

Call

## OptionQuote

Quote of option

### symbol instance-attribute

```python
symbol: str
```

Security code

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### prev\_close instance-attribute

```python
prev_close: Decimal
```

Yesterday's close

### open instance-attribute

```python
open: Decimal
```

Open

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### trade\_status instance-attribute

```python
trade_status: Type[TradeStatus]
```

Security trading status

### implied\_volatility instance-attribute

```python
implied_volatility: Decimal
```

Implied volatility

### open\_interest instance-attribute

```python
open_interest: int
```

Number of open positions

### expiry\_date instance-attribute

```python
expiry_date: date
```

Exprity date

### strike\_price instance-attribute

```python
strike_price: Decimal
```

Strike price

### contract\_multiplier instance-attribute

```python
contract_multiplier: Decimal
```

Contract multiplier

### contract\_type instance-attribute

```python
contract_type: Type[OptionType]
```

Option type

### contract\_size instance-attribute

```python
contract_size: Decimal
```

Contract size

### direction instance-attribute

```python
direction: Type[OptionDirection]
```

Option direction

### historical\_volatility instance-attribute

```python
historical_volatility: Decimal
```

Underlying security historical volatility of the option

### underlying\_symbol instance-attribute

```python
underlying_symbol: str
```

Underlying security symbol of the option

## WarrantType

Warrant type

### Unknown

Bases:

Unknown

### Call

Bases:

Call

### Put

Bases:

Put

### Bull

Bases:

Bull

### Bear

Bases:

Bear

### Inline

Bases:

Inline

## WarrantQuote

Quote of warrant

### symbol instance-attribute

```python
symbol: str
```

Security code

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### prev\_close instance-attribute

```python
prev_close: Decimal
```

Yesterday's close

### open instance-attribute

```python
open: Decimal
```

Open

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### trade\_status instance-attribute

```python
trade_status: Type[TradeStatus]
```

Security trading status

### implied\_volatility instance-attribute

```python
implied_volatility: Decimal
```

Implied volatility

### expiry\_date instance-attribute

```python
expiry_date: date
```

Exprity date

### last\_trade\_date instance-attribute

```python
last_trade_date: date
```

Last tradalbe date

### outstanding\_ratio instance-attribute

```python
outstanding_ratio: Decimal
```

Outstanding ratio

### outstanding\_quantity instance-attribute

```python
outstanding_quantity: int
```

Outstanding quantity

### conversion\_ratio instance-attribute

```python
conversion_ratio: Decimal
```

Conversion ratio

### category instance-attribute

```python
category: Type[WarrantType]
```

Warrant type

### strike\_price instance-attribute

```python
strike_price: Decimal
```

Strike price

### upper\_strike\_price instance-attribute

```python
upper_strike_price: Decimal
```

Upper bound price

### lower\_strike\_price instance-attribute

```python
lower_strike_price: Decimal
```

Lower bound price

### call\_price instance-attribute

```python
call_price: Decimal
```

Call price

### underlying\_symbol instance-attribute

```python
underlying_symbol: str
```

Underlying security symbol of the warrant

## Depth

Depth

### position instance-attribute

```python
position: int
```

Position

### price instance-attribute

```python
price: Optional[Decimal]
```

Price

### volume instance-attribute

```python
volume: int
```

Volume

### order\_num instance-attribute

```python
order_num: int
```

Number of orders

## SecurityDepth

Security depth

### asks instance-attribute

```python
asks: List[Depth]
```

Ask depth

### bids instance-attribute

```python
bids: List[Depth]
```

Bid depth

## Brokers

Brokers

### position instance-attribute

```python
position: int
```

Position

### broker\_ids instance-attribute

```python
broker_ids: List[int]
```

Broker IDs

## SecurityBrokers

Security brokers

### ask\_brokers instance-attribute

```python
ask_brokers: List[Brokers]
```

Ask brokers

### bid\_brokers instance-attribute

```python
bid_brokers: List[Brokers]
```

Bid brokers

## ParticipantInfo

Participant info

### broker\_ids instance-attribute

```python
broker_ids: List[int]
```

Broker IDs

### name\_cn instance-attribute

```python
name_cn: str
```

Participant name (zh-CN)

### name\_en instance-attribute

```python
name_en: str
```

Participant name (en)

### name\_hk instance-attribute

```python
name_hk: str
```

Participant name (zh-HK)

## TradeDirection

Trade direction

### Neutral

Bases:

Neutral

### Down

Bases:

Down

### Up

Bases:

Up

## TradeSession

Trade session

### Intraday

Bases:

Intraday

### Pre

Bases:

Pre-Market

### Post

Bases:

Post-Market

### Overnight

Bases:

Overnight

## Trade

Trade

### price instance-attribute

```python
price: Decimal
```

Price

### volume instance-attribute

```python
volume: int
```

Volume

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of trading

### trade\_type instance-attribute

```python
trade_type: str
```

Trade type

HK

- `*` - Overseas trade
- `D` - Odd-lot trade
- `M` - Non-direct off-exchange trade
- `P` - Late trade (Off-exchange previous day)
- `U` - Auction trade
- `X` - Direct off-exchange trade
- `Y` - Automatch internalized
- `<empty string>` - Automatch normal

US

- `<empty string>` - Regular sale
- `A` - Acquisition
- `B` - Bunched trade
- `D` - Distribution
- `F` - Intermarket sweep
- `G` - Bunched sold trades
- `H` - Price variation trade
- `I` - Odd lot trade
- `K` - Rule 155 trde(NYSE MKT)
- `M` - Market center close price
- `P` - Prior reference price
- `Q` - Market center open price
- `S` - Split trade
- `V` - Contingent trade
- `W` - Average price trade
- `X` - Cross trade
- `1` - Stopped stock(Regular trade)

### direction instance-attribute

```python
direction: Type[TradeDirection]
```

Trade direction

### trade\_session instance-attribute

```python
trade_session: Type[TradeSession]
```

Trade session

## IntradayLine

Intraday line

### price instance-attribute

```python
price: Decimal
```

Close price of the minute

### timestamp instance-attribute

```python
timestamp: datetime
```

Start time of the minute

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### avg\_price instance-attribute

```python
avg_price: Decimal
```

Average price

## Candlestick

Candlestick

### close instance-attribute

```python
close: Decimal
```

Close price

### open instance-attribute

```python
open: Decimal
```

Open price

### low instance-attribute

```python
low: Decimal
```

Low price

### high instance-attribute

```python
high: Decimal
```

High price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### timestamp instance-attribute

```python
timestamp: datetime
```

Timestamp

### trade\_session instance-attribute

```python
trade_session: TradeSession
```

Trade session

## AdjustType

Candlestick adjustment type

### NoAdjust

Bases:

Actual

### ForwardAdjust

Bases:

Adjust forward

## Period

Candlestick period

### Unknown

Bases:

Unknown

### Min\_1

Bases:

One Minute

### Min\_2

Bases:

Two Minutes

### Min\_3

Bases:

Three Minutes

### Min\_5

Bases:

Five Minutes

### Min\_10

Bases:

Ten Minutes

### Min\_15

Bases:

Fifteen Minutes

### Min\_20

Bases:

Twenty Minutes

### Min\_30

Bases:

Thirty Minutes

### Min\_45

Bases:

Forty-Five Minutes

### Min\_60

Bases:

Sixty Minutes

### Min\_120

Bases:

Two Hours

### Min\_180

Bases:

Three Hours

### Min\_240

Bases:

Four Hours

### Day

Bases:

Daily

### Week

Bases:

Weekly

### Month

Bases:

Monthly

### Quarter

Bases:

Quarterly

### Year

Bases:

Yearly

## StrikePriceInfo

Strike price info

### price instance-attribute

```python
price: Decimal
```

Strike price

### call\_symbol instance-attribute

```python
call_symbol: str
```

Security code of call option

### put\_symbol instance-attribute

```python
put_symbol: str
```

Security code of put option

### standard instance-attribute

```python
standard: bool
```

Is standard

## IssuerInfo

Issuer info

### issuer\_id instance-attribute

```python
issuer_id: int
```

Issuer ID

### name\_cn instance-attribute

```python
name_cn: str
```

Issuer name (zh-CN)

### name\_en instance-attribute

```python
name_en: str
```

Issuer name (en)

### name\_hk instance-attribute

```python
name_hk: str
```

Issuer name (zh-HK)

## WarrantStatus

Warrant status

### Suspend

Bases:

Suspend

### PrepareList

Bases:

Prepare List

### Normal

Bases:

Normal

## SortOrderType

Sort order type

### Ascending

Bases:

Ascending

### Descending

Bases:

Descending

## WarrantSortBy

Warrant sort by

### LastDone

Bases:

LastDone

### ChangeRate

Bases:

Change rate

### ChangeValue

Bases:

Change value

### Volume

Bases:

Volume

### Turnover

Bases:

Turnover

### ExpiryDate

Bases:

Expiry date

### StrikePrice

Bases:

Strike price

### UpperStrikePrice

Bases:

Upper strike price

### LowerStrikePrice

Bases:

Lower strike price

### OutstandingQuantity

Bases:

Outstanding quantity

### OutstandingRatio

Bases:

Outstanding ratio

### Premium

Bases:

Premium

### ItmOtm

Bases:

In/out of the bound

### ImpliedVolatility

Bases:

Implied volatility

### Delta

Bases:

Greek value delta

### CallPrice

Bases:

Call price

### ToCallPrice

Bases:

Price interval from the call price

### EffectiveLeverage

Bases:

Effective leverage

### LeverageRatio

Bases:

Leverage ratio

### ConversionRatio

Bases:

Conversion ratio

### BalancePoint

Bases:

Breakeven point

### Status

Bases:

Status

## FilterWarrantExpiryDate

Filter warrant expiry date type

### LT\_3

Bases:

Less than 3 months

### Between\_3\_6

Bases:

3 - 6 months

### Between\_6\_12

Bases:

6 - 12 months

### GT\_12

Bases:

Greater than 12 months

## FilterWarrantInOutBoundsType

Filter warrant in/out of the bounds type

### In

Bases:

In bounds

### Out

Bases:

Out bounds

## WarrantInfo

Warrant info

### symbol instance-attribute

```python
symbol: str
```

Security code

### warrant\_type instance-attribute

```python
warrant_type: Type[WarrantType]
```

Warrant type

### name instance-attribute

```python
name: str
```

Security name

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### change\_rate instance-attribute

```python
change_rate: Decimal
```

Quote change rate

### change\_value instance-attribute

```python
change_value: Decimal
```

Quote change

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### expiry\_date instance-attribute

```python
expiry_date: date
```

Expiry date

### strike\_price instance-attribute

```python
strike_price: Optional[Decimal]
```

Strike price

### upper\_strike\_price instance-attribute

```python
upper_strike_price: Optional[Decimal]
```

Upper strike price

### lower\_strike\_price instance-attribute

```python
lower_strike_price: Optional[Decimal]
```

Lower strike price

### outstanding\_qty instance-attribute

```python
outstanding_qty: int
```

Outstanding quantity

### outstanding\_ratio instance-attribute

```python
outstanding_ratio: Decimal
```

Outstanding ratio

### premium instance-attribute

```python
premium: Decimal
```

Premium

### itm\_otm instance-attribute

```python
itm_otm: Optional[Decimal]
```

In/out of the bound

### implied\_volatility instance-attribute

```python
implied_volatility: Optional[Decimal]
```

Implied volatility

### delta instance-attribute

```python
delta: Optional[Decimal]
```

Greek value delta

### call\_price instance-attribute

```python
call_price: Optional[Decimal]
```

Call price

### to\_call\_price instance-attribute

```python
to_call_price: Optional[Decimal]
```

Price interval from the call price

### effective\_leverage instance-attribute

```python
effective_leverage: Optional[Decimal]
```

Effective leverage

### leverage\_ratio instance-attribute

```python
leverage_ratio: Decimal
```

Leverage ratio

### conversion\_ratio instance-attribute

```python
conversion_ratio: Optional[Decimal]
```

Conversion ratio

### balance\_point instance-attribute

```python
balance_point: Optional[Decimal]
```

Breakeven point

### status instance-attribute

```python
status: Type[WarrantStatus]
```

Status

## TradingSessionInfo

The information of trading session

### begin\_time instance-attribute

```python
begin_time: time
```

Being trading time

### end\_time instance-attribute

```python
end_time: time
```

End trading time

### trade\_session instance-attribute

```python
trade_session: Type[TradeSession]
```

Trading sessions

## MarketTradingSession

Market trading session

### market instance-attribute

```python
market: Type[Market]
```

Market

### trade\_sessions instance-attribute

```python
trade_sessions: List[TradingSessionInfo]
```

Trading session

## MarketTradingDays

### trading\_days instance-attribute

```python
trading_days: List[date]
```

### half\_trading\_days instance-attribute

```python
half_trading_days: List[date]
```

## CapitalFlowLine

Capital flow line

### inflow instance-attribute

```python
inflow: Decimal
```

Inflow capital data

### timestamp instance-attribute

```python
timestamp: datetime
```

Time

## CapitalDistribution

Capital distribution

### large instance-attribute

```python
large: Decimal
```

Large order

### medium instance-attribute

```python
medium: Decimal
```

Medium order

### small instance-attribute

```python
small: Decimal
```

Small order

## CapitalDistributionResponse

Capital distribution response

### timestamp instance-attribute

```python
timestamp: datetime
```

Time

### capital\_in instance-attribute

```python
capital_in: CapitalDistribution
```

Inflow capital data

### capital\_out instance-attribute

```python
capital_out: CapitalDistribution
```

Outflow capital data

## WatchlistSecurity

Watchlist security

### symbol instance-attribute

```python
symbol: str
```

Security symbol

### market instance-attribute

```python
market: Market
```

Market

### name instance-attribute

```python
name: str
```

Security name

### watched\_price instance-attribute

```python
watched_price: Optional[Decimal]
```

Watched price

### watched\_at instance-attribute

```python
watched_at: datetime
```

Watched time

## WatchlistGroup

### id instance-attribute

```python
id: int
```

Group id

### name instance-attribute

```python
name: str
```

Group name

### securities instance-attribute

```python
securities: List[WatchlistSecurity]
```

Securities

## SecuritiesUpdateMode

Securities update mode

### Add

Bases:

Add securities

### Remove

Bases:

Remove securities

### Replace

Bases:

Replace securities

## RealtimeQuote

Real-time quote

### symbol instance-attribute

```python
symbol: str
```

Security code

### last\_done instance-attribute

```python
last_done: Decimal
```

Latest price

### open instance-attribute

```python
open: Decimal
```

Open

### high instance-attribute

```python
high: Decimal
```

High

### low instance-attribute

```python
low: Decimal
```

Low

### timestamp instance-attribute

```python
timestamp: datetime
```

Time of latest price

### volume instance-attribute

```python
volume: int
```

Volume

### turnover instance-attribute

```python
turnover: Decimal
```

Turnover

### trade\_status instance-attribute

```python
trade_status: Type[TradeStatus]
```

Security trading status

## Subscription

Subscription

### symbol instance-attribute

```python
symbol: str
```

Security code

### sub\_types instance-attribute

```python
sub_types: List[Type[SubType]]
```

Subscription types

### candlesticks instance-attribute

```python
candlesticks: List[Type[Period]]
```

Candlesticks

## CalcIndex

Calc index

### LastDone

Bases:

Latest price

### ChangeValue

Bases:

Change value

### ChangeRate

Bases:

Change rate

### Volume

Bases:

Volume

### Turnover

Bases:

Turnover

### YtdChangeRate

Bases:

Year-to-date change ratio

### TurnoverRate

Bases:

Turnover rate

### TotalMarketValue

Bases:

Total market value

### CapitalFlow

Bases:

Capital flow

### Amplitude

Bases:

Amplitude

### VolumeRatio

Bases:

Volume ratio

### PeTtmRatio

Bases:

PE (TTM)

### PbRatio

Bases:

PB

### DividendRatioTtm

Bases:

Dividend ratio (TTM)

### FiveDayChangeRate

Bases:

Five days change ratio

### TenDayChangeRate

Bases:

Ten days change ratio

### HalfYearChangeRate

Bases:

Half year change ratio

### FiveMinutesChangeRate

Bases:

Five minutes change ratio

### ExpiryDate

Bases:

Expiry date

### StrikePrice

Bases:

Strike price

### UpperStrikePrice

Bases:

Upper bound price

### LowerStrikePrice

Bases:

Lower bound price

### OutstandingQty

Bases:

Outstanding quantity

### OutstandingRatio

Bases:

Outstanding ratio

### Premium

Bases:

Premium

### ItmOtm

Bases:

In/out of the bound

### ImpliedVolatility

Bases:

Implied volatility

### WarrantDelta

Bases:

Warrant delta

### CallPrice

Bases:

Call price

### ToCallPrice

Bases:

Price interval from the call price

### EffectiveLeverage

Bases:

Effective leverage

### LeverageRatio

Bases:

Leverage ratio

### ConversionRatio

Bases:

Conversion ratio

### BalancePoint

Bases:

Breakeven point

### OpenInterest

Bases:

Open interest

### Delta

Bases:

Delta

### Gamma

Bases:

Gamma

### Theta

Bases:

Theta

### Vega

Bases:

Vega

### Rho

Bases:

Rho

## SecurityCalcIndex

Security calc index response

### symbol instance-attribute

```python
symbol: str
```

Security symbol

### last\_done instance-attribute

```python
last_done: Optional[Decimal]
```

Latest price

### change\_value instance-attribute

```python
change_value: Optional[Decimal]
```

Change value

### change\_rate instance-attribute

```python
change_rate: Optional[Decimal]
```

Change ratio

### volume instance-attribute

```python
volume: Optional[int]
```

Volume

### turnover instance-attribute

```python
turnover: Optional[Decimal]
```

Turnover

### ytd\_change\_rate instance-attribute

```python
ytd_change_rate: Optional[Decimal]
```

Year-to-date change ratio

### turnover\_rate instance-attribute

```python
turnover_rate: Optional[Decimal]
```

turnover\_rate

### total\_market\_value instance-attribute

```python
total_market_value: Optional[Decimal]
```

Total market value

### capital\_flow instance-attribute

```python
capital_flow: Optional[Decimal]
```

Capital flow

### amplitude instance-attribute

```python
amplitude: Optional[Decimal]
```

Amplitude

### volume\_ratio instance-attribute

```python
volume_ratio: Optional[Decimal]
```

Volume ratio

### pe\_ttm\_ratio instance-attribute

```python
pe_ttm_ratio: Optional[Decimal]
```

PE (TTM)

### pb\_ratio instance-attribute

```python
pb_ratio: Optional[Decimal]
```

PB

### dividend\_ratio\_ttm instance-attribute

```python
dividend_ratio_ttm: Optional[Decimal]
```

Dividend ratio (TTM)

### five\_day\_change\_rate instance-attribute

```python
five_day_change_rate: Optional[Decimal]
```

Five days change ratio

### ten\_day\_change\_rate instance-attribute

```python
ten_day_change_rate: Optional[Decimal]
```

Ten days change ratio

### half\_year\_change\_rate instance-attribute

```python
half_year_change_rate: Optional[Decimal]
```

Half year change ratio

### five\_minutes\_change\_rate instance-attribute

```python
five_minutes_change_rate: Optional[Decimal]
```

Five minutes change ratio

### expiry\_date instance-attribute

```python
expiry_date: Optional[date]
```

Expiry date

### strike\_price instance-attribute

```python
strike_price: Optional[Decimal]
```

Strike price

### upper\_strike\_price instance-attribute

```python
upper_strike_price: Optional[Decimal]
```

Upper bound price

### lower\_strike\_price instance-attribute

```python
lower_strike_price: Optional[Decimal]
```

Lower bound price

### outstanding\_qty instance-attribute

```python
outstanding_qty: Optional[int]
```

Outstanding quantity

### outstanding\_ratio instance-attribute

```python
outstanding_ratio: Optional[Decimal]
```

Outstanding ratio

### premium instance-attribute

```python
premium: Optional[Decimal]
```

Premium

### itm\_otm instance-attribute

```python
itm_otm: Optional[Decimal]
```

In/out of the bound

### implied\_volatility instance-attribute

```python
implied_volatility: Optional[Decimal]
```

Implied volatility

### warrant\_delta instance-attribute

```python
warrant_delta: Optional[Decimal]
```

Warrant delta

### call\_price instance-attribute

```python
call_price: Optional[Decimal]
```

Call price

### to\_call\_price instance-attribute

```python
to_call_price: Optional[Decimal]
```

Price interval from the call price

### effective\_leverage instance-attribute

```python
effective_leverage: Optional[Decimal]
```

Effective leverage

### leverage\_ratio instance-attribute

```python
leverage_ratio: Optional[Decimal]
```

Leverage ratio

### conversion\_ratio instance-attribute

```python
conversion_ratio: Optional[Decimal]
```

Conversion ratio

### balance\_point instance-attribute

```python
balance_point: Optional[Decimal]
```

Breakeven point

### open\_interest instance-attribute

```python
open_interest: Optional[int]
```

Open interest

### delta instance-attribute

```python
delta: Optional[Decimal]
```

Delta

### gamma instance-attribute

```python
gamma: Optional[Decimal]
```

Gamma

### theta instance-attribute

```python
theta: Optional[Decimal]
```

Theta

### vega instance-attribute

```python
vega: Optional[Decimal]
```

Vega

### rho instance-attribute

```python
rho: Optional[Decimal]
```

Rho

## QuotePackageDetail

Quote package detail

### key instance-attribute

```python
key: str
```

Key

### name instance-attribute

```python
name: str
```

Name

### description instance-attribute

```python
description: str
```

Description

### start\_at instance-attribute

```python
start_at: datetime
```

Start time

### end\_at instance-attribute

```python
end_at: datetime
```

End time

## TradeSessions

Trade sessions

### Intraday

Bases:

Intraday

### All

Bases:

All

## MarketTemperature

Market temperature

### temperature instance-attribute

```python
temperature: int
```

Temperature value

### description instance-attribute

```python
description: str
```

Temperature description

### valuation instance-attribute

```python
valuation: int
```

Market valuation

### sentiment instance-attribute

```python
sentiment: int
```

Market sentiment

### timestamp instance-attribute

```python
timestamp: datetime
```

Time

## Granularity

Data granularity

### Unknown

Bases:

Unknown

### Daily

Bases:

Daily

### Weekly

Bases:

Weekly

### Monthly

Bases:

Monthly

## HistoryMarketTemperatureResponse

History market temperature response

### granularity instance-attribute

```python
granularity: Type[Granularity]
```

Granularity

### records instance-attribute

```python
records: List[MarketTemperature]
```

Records

## QuoteContext

Quote context

| Parameters: | - **`config`** () – 	Configuration object |
| --- | --- |

### \_\_init\_\_

```python
__init__(config: Config) -> None
```

### member\_id

```python
member_id() -> int
```

Returns the member ID

### quote\_level

```python
quote_level() -> str
```

Returns the quote level

### quote\_package\_details

```python
quote_package_details() -> List[QuotePackageDetail]
```

Returns the quote package details

### set\_on\_quote

```python
set_on_quote(callback: Callable[[str, PushQuote], None]) -> None
```

Set quote callback, after receiving the quote data push, it will call back to this function.

### set\_on\_depth

```python
set_on_depth(callback: Callable[[str, PushDepth], None]) -> None
```

Set depth callback, after receiving the depth data push, it will call back to this function.

### set\_on\_brokers

```python
set_on_brokers(callback: Callable[[str, PushBrokers], None]) -> None
```

Set brokers callback, after receiving the brokers data push, it will call back to this function.

### set\_on\_trades

```python
set_on_trades(callback: Callable[[str, PushTrades], None]) -> None
```

Set trades callback, after receiving the trades data push, it will call back to this function.

### set\_on\_candlestick

```python
set_on_candlestick(callback: Callable[[str, PushCandlestick], None]) -> None
```

Set candlestick callback, after receiving the candlestick updated event, it will call back to this function.

### subscribe

```python
subscribe(symbols: List[str], sub_types: List[Type[SubType]], is_first_push: bool = False) -> None
```

Subscribe

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes - **`sub_types`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`) – - **`is_first_push`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`, default: `False`) – 	Whether to perform a data push immediately after subscribing. (trade not supported) |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, SubType, PushQuote

def on_quote(symbol: str, event: PushQuote):
    print(symbol, event)

config = Config.from_env()
ctx = QuoteContext(config)
ctx.set_on_quote(on_quote)

ctx.subscribe(["700.HK", "AAPL.US"], [
              SubType.Quote], is_first_push = True)
sleep(30)
```

### unsubscribe

```python
unsubscribe(symbols: List[str], sub_types: List[Type[SubType]]) -> None
```

Unsubscribe

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes - **`sub_types`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`) – |
| --- | --- |

Examples:

::

```java
from longport.openapi import QuoteContext, Config, SubType
config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe(["700.HK", "AAPL.US"], [SubType.Quote])
ctx.unsubscribe(["AAPL.US"], [SubType.Quote])
```

### subscribe\_candlesticks

```python
subscribe_candlesticks(symbol: str, period: Type[Period], trade_sessions: Type[TradeSessions] = TradeSessions.Intraday) -> List[Candlestick]
```

Subscribe security candlesticks

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`period`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Period type - **`trade_sessions`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`, default: ) – 	Trade sessions |
| --- | --- |

Examples:

::

```python
from longport.openapi import QuoteContext, Config, PushCandlestick, TradeSessions
config = Config.from_env()
ctx = QuoteContext(config)

def on_candlestick(symbol: str, event: PushCandlestick):
    print(symbol, event)

ctx.set_on_candlestick(on_candlestick)
ctx.subscribe_candlesticks("700.HK", Period.Min_1, TradeSessions.Intraday)
sleep(30)
```

### static\_info

```python
static_info(symbols: List[str]) -> List[SecurityStaticInfo]
```

Get basic information of securities

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Security info list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.static_info(
    ["700.HK", "AAPL.US", "TSLA.US", "NFLX.US"])
print(resp)
```

### quote

```python
quote(symbols: List[str]) -> List[SecurityQuote]
```

Get quote of securities

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Security quote list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.quote(["700.HK", "AAPL.US", "TSLA.US", "NFLX.US"])
print(resp)
```

### option\_quote

```python
option_quote(symbols: List[str]) -> List[OptionQuote]
```

Get quote of option securities

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Option quote list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.option_quote(["AAPL230317P160000.US"])
print(resp)
```

### warrant\_quote

```python
warrant_quote(symbols: List[str]) -> List[WarrantQuote]
```

Get quote of warrant securities

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Warrant quote list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.warrant_quote(["21125.HK"])
print(resp)
```

### depth

```python
depth(symbol: str) -> SecurityDepth
```

Get security depth

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - – 	Security depth |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.depth("700.HK")
print(resp)
```

### brokers

```python
brokers(symbol: str) -> SecurityBrokers
```

Get security brokers

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - – 	Security brokers |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.brokers("700.HK")
print(resp)
```

### participants

```python
participants() -> List[ParticipantInfo]
```

Get participants

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Participants |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.participants()
print(resp)
```

### trades

```python
trades(symbol: str, count: int) -> List[Trade]
```

Get security trades

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`count`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Count of trades (Maximum is `1000`) |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Trades |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.trades("700.HK", 10)
print(resp)
```

### intraday

```python
intraday(symbol: str) -> List[IntradayLine]
```

Get security intraday lines

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Intraday lines |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.intraday("700.HK")
print(resp)
```

### candlesticks

```python
candlesticks(symbol: str, period: Type[Period], count: int, adjust_type: Type[AdjustType], trade_sessions: Type[TradeSessions] = TradeSessions.Intraday) -> List[Candlestick]
```

Get security candlesticks

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`period`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Candlestick period - **`count`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Count of cancdlestick (Maximum is `1000`) - **`adjust_type`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Adjustment type - **`trade_sessions`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`, default: ) – 	Trade sessions |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Candlesticks |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config, Period, AdjustType, TradeSessions

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.candlesticks(
    "700.HK", Period.Day, 10, AdjustType.NoAdjust, TradeSessions.Intraday)
print(resp)
```

### history\_candlesticks\_by\_offset

```python
history_candlesticks_by_offset(symbol: str, period: Type[Period], adjust_type: Type[AdjustType], forward: bool, count: int, time: Optional[datetime] = None, trade_sessions: Type[TradeSessions] = TradeSessions.Intraday) -> List[Candlestick]
```

Get security history candlesticks by offset

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`period`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Period type - **`adjust_type`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Adjust type - **`forward`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`) – 	If `True`, query the latest from the specified time - **`count`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Count of candlesticks - **`time`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	Datetime - **`trade_sessions`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`, default: ) – 	Trade sessions |
| --- | --- |

### history\_candlesticks\_by\_date

```python
history_candlesticks_by_date(symbol: str, period: Type[Period], adjust_type: Type[AdjustType], start: Optional[date], end: Optional[date], trade_sessions: Type[TradeSessions] = TradeSessions.Intraday) -> List[Candlestick]
```

Get security history candlesticks by date

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`period`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Period type - **`adjust_type`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Adjust type - **`start`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")]`) – 	Start date - **`end`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")]`) – 	End date - **`trade_sessions`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`, default: ) – 	Trade sessions |
| --- | --- |

### option\_chain\_expiry\_date\_list

```python
option_chain_expiry_date_list(symbol: str) -> List[date]
```

Get option chain expiry date list

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")]` – 	Option chain expiry date list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.option_chain_expiry_date_list("AAPL.US")
print(resp)
```

### option\_chain\_info\_by\_date

```python
option_chain_info_by_date(symbol: str, expiry_date: date) -> List[StrikePriceInfo]
```

Get option chain info by date

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`expiry_date`** (`[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")`) – 	Expiry date |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Option chain info |
| --- | --- |

Examples:

::

```lua
from datetime import date
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.option_chain_info_by_date(
    "AAPL.US", date(2023, 1, 20))
print(resp)
```

### warrant\_issuers

```python
warrant_issuers() -> List[IssuerInfo]
```

Get warrant issuers

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Warrant issuers |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.warrant_issuers()
print(resp)
```

### warrant\_list

```python
warrant_list(symbol: str, sort_by: Type[WarrantSortBy], sort_order: Type[SortOrderType], warrant_type: Optional[List[Type[WarrantType]]] = None, issuer: Optional[List[int]] = None, expiry_date: Optional[List[Type[FilterWarrantExpiryDate]]] = None, price_type: Optional[List[Type[FilterWarrantInOutBoundsType]]] = None, status: Optional[List[Type[WarrantStatus]]] = None) -> List[WarrantInfo]
```

Get warrant list

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`sort_by`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Sort by field - **`sort_order`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Sort order - **`warrant_type`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by warrant type - **`issuer`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[int](https://docs.python.org/3/library/functions.html#int)]]`, default: `None`) – 	Filter by issuer - **`expiry_date`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by expiry date - **`price_type`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by price type - **`status`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by status |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Warrant list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config, WarrantSortBy, SortOrderType

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.warrant_list("700.HK", WarrantSortBy.LastDone, SortOrderType.Ascending)
print(resp)
```

### trading\_session

```python
trading_session() -> List[MarketTradingSession]
```

Get trading session of the day

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Trading session of the day |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.trading_session()
print(resp)
```

### trading\_days

```python
trading_days(market: Type[Market], begin: date, end: date) -> MarketTradingDays
```

Get trading session of the day

The interval must be less than one month, and only the most recent year is supported.

| Parameters: | - **`market`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Market - **`begin`** (`[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")`) – 	Begin date - **`end`** (`[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")`) – 	End date |
| --- | --- |

| Returns: | - – 	Trading days |
| --- | --- |

Examples:

::

```lua
from datetime import date
from longport.openapi import QuoteContext, Config, Market

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.trading_days(
    Market.HK, date(2022, 1, 1), date(2022, 2, 1))
print(resp)
```

### capital\_flow

```python
capital_flow(symbol: str) -> List[CapitalFlowLine]
```

Get capital flow intraday

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Capital flow list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.capital_flow("700.HK")
print(resp)
```

### capital\_distribution

```python
capital_distribution(symbol: str) -> CapitalDistributionResponse
```

Get capital distribution

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - – 	Capital distribution |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.capital_distribution("700.HK")
print(resp)
```

### calc\_indexes

```python
calc_indexes(symbols: List[str], indexes: List[Type[CalcIndex]]) -> List[SecurityCalcIndex]
```

Get calc indexes

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes - **`indexes`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`) – 	Calc indexes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Calc indexes of the symbols |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config, CalcIndex

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.calc_indexes(["700.HK", "APPL.US"], [CalcIndex.LastDone, CalcIndex.ChangeRate])
print(resp)
```

### watchlist

```python
watchlist() -> List[WatchlistGroup]
```

Get watch list

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Watch list groups |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.watchlist()
print(resp)
```

### create\_watchlist\_group

```python
create_watchlist_group(name: str, securities: Optional[List[str]] = None) -> int
```

Create watchlist group

| Parameters: | - **`name`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Group name - **`securities`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]]`, default: `None`) – 	Securities |
| --- | --- |

| Returns: | - `[int](https://docs.python.org/3/library/functions.html#int)` – 	Group ID |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)
group_id = ctx.create_watchlist_group(name = "Watchlist1", securities = ["700.HK", "AAPL.US"])
print(group_id)
```

### delete\_watchlist\_group

```python
delete_watchlist_group(id: int, purge: bool = False)
```

Delete watchlist group

| Parameters: | - **`id`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Group ID - **`purge`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`, default: `False`) – 	Move securities in this group to the default group |
| --- | --- |

Examples:

::

```java
from longport.openapi import QuoteContext, Config

config = Config.from_env()
ctx = QuoteContext(config)
ctx.delete_watchlist_group(10086)
```

### update\_watchlist\_group

```python
update_watchlist_group(id: int, name: Optional[str] = None, securities: Optional[List[str]] = None, mode: Optional[Type[SecuritiesUpdateMode]] = None)
```

Update watchlist group

| Parameters: | - **`id`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Group ID - **`name`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Group name - **`securities`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]]`, default: `None`) – 	Securities |
| --- | --- |

Examples:

::

```java
from longport.openapi import QuoteContext, Config, SecuritiesUpdateMode

config = Config.from_env()
ctx = QuoteContext(config)
ctx.update_watchlist_group(10086, name = "Watchlist2", securities = ["700.HK", "AAPL.US"], SecuritiesUpdateMode.Replace)
```

### security\_list

```python
security_list(market: Type[Market], category: Type[SecurityListCategory]) -> List[Security]
```

Get security list

| Parameters: | - **`market`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Market - **`category`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Security list category |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Security list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config, Market, SecurityListCategory

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.security_list(Market.HK, SecurityListCategory.Overnight)
print(resp)
```

### market\_temperature

```python
market_temperature(market: Type[Market]) -> MarketTemperature
```

Get current market temperature

| Parameters: | - **`market`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Market |
| --- | --- |

| Returns: | - – 	Market temperature |
| --- | --- |

Examples:

::

```lua
from longport.openapi import QuoteContext, Config, Market

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.market_temperature(Market.HK)
print(resp)
```

### history\_market\_temperature

```python
history_market_temperature(market: Type[Market], start: date, end: date) -> HistoryMarketTemperatureResponse
```

Get historical market temperature

| Parameters: | - **`market`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Market - **`start`** (`[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")`) – 	Start date - **`end`** (`[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")`) – 	End date |
| --- | --- |

| Returns: | - – 	History market temperature |
| --- | --- |

Examples:

::

```lua
from datetime import date
from longport.openapi import QuoteContext, Config, Market

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.history_market_temperature(Market.HK, date(2023, 1, 1), date(2023, 1, 31))
print(resp)
```

### realtime\_quote

```python
realtime_quote(symbols: List[str]) -> List[RealtimeQuote]
```

Get real-time quote

Get real-time quotes of the subscribed symbols, it always returns the data in the local storage.

| Parameters: | - **`symbols`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`) – 	Security codes |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Quote list |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, SubType

config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe(["700.HK", "AAPL.US"], [
              SubType.Quote], is_first_push = True)
sleep(5)
resp = ctx.realtime_quote(["700.HK", "AAPL.US"])
print(resp)
```

### realtime\_depth

```python
realtime_depth(symbol: str) -> SecurityDepth
```

Get real-time depth

Get real-time depth of the subscribed symbols, it always returns the data in the local storage.

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - – 	Security depth |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, SubType

config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe(["700.HK", "AAPL.US"], [
              SubType.Depth], is_first_push = True)
sleep(5)
resp = ctx.realtime_depth("700.HK")
print(resp)
```

### realtime\_brokers

```python
realtime_brokers(symbol: str) -> SecurityBrokers
```

Get real-time brokers

Get real-time brokers of the subscribed symbols, it always returns the data in the local storage.

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code |
| --- | --- |

| Returns: | - – 	Security brokers |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, SubType

config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe(["700.HK", "AAPL.US"], [
              SubType.Brokers], is_first_push = True)
sleep(5)
resp = ctx.realtime_brokers("700.HK")
print(resp)
```

### realtime\_trades

```python
realtime_trades(symbol: str, count: int) -> List[Trade]
```

Get real-time trades

Get real-time trades of the subscribed symbols, it always returns the data in the local storage.

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`count`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Count of trades |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Security trades |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, SubType

config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe(["700.HK", "AAPL.US"], [
              SubType.Trade], is_first_push = False)
sleep(5)
resp = ctx.realtime_trades("700.HK", 10)
print(resp)
```

### realtime\_candlesticks

```python
realtime_candlesticks(symbol: str, period: Type[Period], count: int) -> List[Candlestick]
```

Get real-time candlesticks

Get Get real-time candlesticks of the subscribed symbols, it always returns the data in the local storage.

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`period`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Period type - **`count`** (`[int](https://docs.python.org/3/library/functions.html#int)`) – 	Count of candlesticks |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Security candlesticks |
| --- | --- |

Examples:

::

```python
from time import sleep
from longport.openapi import QuoteContext, Config, Period

config = Config.from_env()
ctx = QuoteContext(config)

ctx.subscribe_candlesticks("AAPL.US", Period.Min_1)
sleep(5)
resp = ctx.realtime_candlesticks("AAPL.US", Period.Min_1, 10)
print(resp)
```

## OrderSide

Order side

### Unknown

Bases:

Unknown

### Buy

Bases:

Buy

### Sell

Bases:

Sell

## OrderType

Order type

### Unknown

Bases:

Unknown

### LO

Bases:

Limit Order

### ELO

Bases:

Enhanced Limit Order

### MO

Bases:

Market Order

### AO

Bases:

At-auction Order

### ALO

Bases:

At-auction Limit Order

### ODD

Bases:

Odd Lots

### LIT

Bases:

Limit If Touched

### MIT

Bases:

Market If Touched

### TSLPAMT

Bases:

Trailing Limit If Touched (Trailing Amount)

### TSLPPCT

Bases:

Trailing Limit If Touched (Trailing Percent)

### TSMAMT

Bases:

Trailing Market If Touched (Trailing Amount)

### TSMPCT

Bases:

Trailing Market If Touched (Trailing Percent)

### SLO

Bases:

Special Limit Order

## OrderStatus

Order status

### Unknown

Bases:

Unknown

### NotReported

Bases:

Not reported

### ReplacedNotReported

Bases:

Not reported (Replaced Order)

### ProtectedNotReported

Bases:

Not reported (Protected Order)

### VarietiesNotReported

Bases:

Not reported (Conditional Order)

### Filled

Bases:

Filled

### WaitToNew

Bases:

Wait To New

### New

Bases:

New

### WaitToReplace

Bases:

Wait To Replace

### PendingReplace

Bases:

Pending Replace

### Replaced

Bases:

Replaced

### PartialFilled

Bases:

Partial Filled

### WaitToCancel

Bases:

Wait To Cancel

### PendingCancel

Bases:

Pending Cancel

### Rejected

Bases:

Rejected

### Canceled

Bases:

Canceled

### Expired

Bases:

ExpiredStatus

### PartialWithdrawal

Bases:

PartialWithdrawal

## OrderTag

Order tag

### Unknown

Bases:

Unknown

### Normal

Bases:

Normal Order

### LongTerm

Bases:

Long term Order

### Grey

Bases:

Grey Order

### MarginCall

Bases:

Force Selling

### Offline

Bases:

OTC

### Creditor

Bases:

Option Exercise Long

### Debtor

Bases:

Option Exercise Short

### NonExercise

Bases:

Wavier Of Option Exercise

### AllocatedSub

Bases:

Trade Allocation

## TriggerStatus

Trigger status

### Unknown

Bases:

Unknown

### Deactive

Bases:

Deactive

### Active

Bases:

Active

### Released

Bases:

Released

## Execution

Execution

### order\_id instance-attribute

```python
order_id: str
```

Order ID

### trade\_id instance-attribute

```python
trade_id: str
```

Execution ID

### symbol instance-attribute

```python
symbol: str
```

Security code

### trade\_done\_at instance-attribute

```python
trade_done_at: datetime
```

Trade done time

### quantity instance-attribute

```python
quantity: Decimal
```

Executed quantity

### price instance-attribute

```python
price: Decimal
```

Executed price

## PushOrderChanged

Order changed message

### side instance-attribute

```python
side: Type[OrderSide]
```

Order side

### stock\_name instance-attribute

```python
stock_name: str
```

Stock name

### submitted\_quantity instance-attribute

```python
submitted_quantity: Decimal
```

Submitted quantity

### symbol instance-attribute

```python
symbol: str
```

Order symbol

### order\_type instance-attribute

```python
order_type: Type[OrderType]
```

Order type

### submitted\_price instance-attribute

```python
submitted_price: Decimal
```

Submitted price

### executed\_quantity instance-attribute

```python
executed_quantity: Decimal
```

Executed quantity

### executed\_price instance-attribute

```python
executed_price: Optional[Decimal]
```

Executed price

### order\_id instance-attribute

```python
order_id: str
```

Order ID

### currency instance-attribute

```python
currency: str
```

Currency

### status instance-attribute

```python
status: Type[OrderStatus]
```

Order status

### submitted\_at instance-attribute

```python
submitted_at: datetime
```

Submitted time

### updated\_at instance-attribute

```python
updated_at: datetime
```

Last updated time

### trigger\_price instance-attribute

```python
trigger_price: Optional[Decimal]
```

Order trigger price

### msg instance-attribute

```python
msg: str
```

Rejected message or remark

### tag instance-attribute

```python
tag: Type[OrderTag]
```

Order tag

### trigger\_status instance-attribute

```python
trigger_status: Optional[Type[TriggerStatus]]
```

Conditional order trigger status

### trigger\_at instance-attribute

```python
trigger_at: Optional[datetime]
```

Conditional order trigger time

### trailing\_amount instance-attribute

```python
trailing_amount: Optional[Decimal]
```

Trailing amount

### trailing\_percent instance-attribute

```python
trailing_percent: Optional[Decimal]
```

Trailing percent

### limit\_offset instance-attribute

```python
limit_offset: Optional[Decimal]
```

Limit offset amount

### account\_no instance-attribute

```python
account_no: str
```

Account no

### last\_price instance-attribute

```python
last_price: Optional[Decimal]
```

Last price

### remark instance-attribute

```python
remark: str
```

Remark message

## TimeInForceType

Time in force type

### Unknown

Bases:

Unknown

### Day

Bases:

Day Order

### GoodTilCanceled

Bases:

Good Til Canceled Order

### GoodTilDate

Bases:

Good Til Date Order

## OutsideRTH

Enable or disable outside regular trading hours

### Unknown

Bases:

Unknown

### RTHOnly

Bases:

Regular trading hour only

### AnyTime

Bases:

Any time

### Overnight

Bases:

Overnight

## Order

Order

### order\_id instance-attribute

```python
order_id: str
```

Order ID

### status instance-attribute

```python
status: Type[OrderStatus]
```

Order status

### stock\_name instance-attribute

```python
stock_name: str
```

Stock name

### quantity instance-attribute

```python
quantity: Decimal
```

Submitted quantity

### executed\_quantity instance-attribute

```python
executed_quantity: Decimal
```

Executed quantity

### price instance-attribute

```python
price: Optional[Decimal]
```

Submitted price

### executed\_price instance-attribute

```python
executed_price: Optional[Decimal]
```

Executed price

### submitted\_at instance-attribute

```python
submitted_at: datetime
```

Submitted time

### side instance-attribute

```python
side: Type[OrderSide]
```

Order side

### symbol instance-attribute

```python
symbol: str
```

Security code

### order\_type instance-attribute

```python
order_type: Type[OrderType]
```

Order type

### last\_done instance-attribute

```python
last_done: Optional[Decimal]
```

Last done

### trigger\_price instance-attribute

```python
trigger_price: Optional[Decimal]
```

`LIT` / `MIT` Order Trigger Price

### msg instance-attribute

```python
msg: str
```

Rejected Message or remark

### tag instance-attribute

```python
tag: Type[OrderTag]
```

Order tag

### time\_in\_force instance-attribute

```python
time_in_force: Type[TimeInForceType]
```

Time in force type

### expire\_date instance-attribute

```python
expire_date: Optional[date]
```

Long term order expire date

### updated\_at instance-attribute

```python
updated_at: Optional[datetime]
```

Last updated time

### trigger\_at instance-attribute

```python
trigger_at: Optional[datetime]
```

Conditional order trigger time

### trailing\_amount instance-attribute

```python
trailing_amount: Optional[Decimal]
```

`TSMAMT` / `TSLPAMT` order trailing amount

### trailing\_percent instance-attribute

```python
trailing_percent: Optional[Decimal]
```

`TSMPCT` / `TSLPPCT` order trailing percent

### limit\_offset instance-attribute

```python
limit_offset: Optional[Decimal]
```

`TSLPAMT` / `TSLPPCT` order limit offset amount

### trigger\_status instance-attribute

```python
trigger_status: Optional[Type[TriggerStatus]]
```

Conditional order trigger status

### currency instance-attribute

```python
currency: str
```

Currency

### outside\_rth instance-attribute

```python
outside_rth: Optional[Type[OutsideRTH]]
```

Enable or disable outside regular trading hours

### remark instance-attribute

```python
remark: str
```

Remark

## CommissionFreeStatus

Commission-free Status

### Unknown

Bases:

Unknown

### None\_

Bases:

None

### Calculated

Bases:

Commission-free amount to be calculated

### Pending

Bases:

Pending commission-free

### Ready

Bases:

Commission-free applied

## DeductionStatus

Deduction status

### Unknown

Bases:

Unknown

### None\_

Bases:

None

### NoData

Bases:

Settled with no data

### Pending

Bases:

Settled and pending distribution

### Done

Bases:

Settled and distributed

## ChargeCategoryCode

Charge category code

### Unknown

Bases:

Unknown

### Broker

Bases:

Broker

### Third

Bases:

Third

## OrderHistoryDetail

Order history detail

### price instance-attribute

```python
price: Decimal
```

Executed price for executed orders, submitted price for expired, canceled, rejected orders, etc.

### quantity instance-attribute

```python
quantity: Decimal
```

Executed quantity for executed orders, remaining quantity for expired, canceled, rejected orders, etc.

### status instance-attribute

```python
status: Type[OrderStatus]
```

Order status

### msg instance-attribute

```python
msg: str
```

Execution or error message

### time instance-attribute

```python
time: datetime
```

Occurrence time

## OrderChargeFee

Order charge fee

### code instance-attribute

```python
code: str
```

Charge code

### name instance-attribute

```python
name: str
```

Charge name

### amount instance-attribute

```python
amount: Decimal
```

Charge amount

### currency instance-attribute

```python
currency: str
```

Charge currency

## OrderChargeItem

Order charge item

### code instance-attribute

```python
code: Type[ChargeCategoryCode]
```

Charge category code

### name instance-attribute

```python
name: str
```

Charge category name

### fees instance-attribute

```python
fees: List[OrderChargeFee]
```

Charge details

## OrderChargeDetail

Order charge detail

### total\_amount instance-attribute

```python
total_amount: Decimal
```

Total charges amount

### currency instance-attribute

```python
currency: str
```

Settlement currency

### items instance-attribute

```python
items: List[OrderChargeItem]
```

Order charge items

## OrderDetail

Order detail

### order\_id instance-attribute

```python
order_id: str
```

Order ID

### status instance-attribute

```python
status: Type[OrderStatus]
```

Order status

### stock\_name instance-attribute

```python
stock_name: str
```

Stock name

### quantity instance-attribute

```python
quantity: Decimal
```

Submitted quantity

### executed\_quantity instance-attribute

```python
executed_quantity: Decimal
```

Executed quantity

### price instance-attribute

```python
price: Optional[Decimal]
```

Submitted price

### executed\_price instance-attribute

```python
executed_price: Optional[Decimal]
```

Executed price

### submitted\_at instance-attribute

```python
submitted_at: datetime
```

Submitted time

### side instance-attribute

```python
side: Type[OrderSide]
```

Order side

### symbol instance-attribute

```python
symbol: str
```

Security code

### order\_type instance-attribute

```python
order_type: Type[OrderType]
```

Order type

### last\_done instance-attribute

```python
last_done: Optional[Decimal]
```

Last done

### trigger\_price instance-attribute

```python
trigger_price: Optional[Decimal]
```

`LIT` / `MIT` Order Trigger Price

### msg instance-attribute

```python
msg: str
```

Rejected Message or remark

### tag instance-attribute

```python
tag: Type[OrderTag]
```

Order tag

### time\_in\_force instance-attribute

```python
time_in_force: Type[TimeInForceType]
```

Time in force type

### expire\_date instance-attribute

```python
expire_date: Optional[date]
```

Long term order expire date

### updated\_at instance-attribute

```python
updated_at: Optional[datetime]
```

Last updated time

### trigger\_at instance-attribute

```python
trigger_at: Optional[datetime]
```

Conditional order trigger time

### trailing\_amount instance-attribute

```python
trailing_amount: Optional[Decimal]
```

`TSMAMT` / `TSLPAMT` order trailing amount

### trailing\_percent instance-attribute

```python
trailing_percent: Optional[Decimal]
```

`TSMPCT` / `TSLPPCT` order trailing percent

### limit\_offset instance-attribute

```python
limit_offset: Optional[Decimal]
```

`TSLPAMT` / `TSLPPCT` order limit offset amount

### trigger\_status instance-attribute

```python
trigger_status: Optional[Type[TriggerStatus]]
```

Conditional order trigger status

### currency instance-attribute

```python
currency: str
```

Currency

### outside\_rth instance-attribute

```python
outside_rth: Optional[Type[OutsideRTH]]
```

Enable or disable outside regular trading hours

### remark instance-attribute

```python
remark: str
```

Remark

### free\_status instance-attribute

```python
free_status: Type[CommissionFreeStatus]
```

Commission-free Status

### free\_amount instance-attribute

```python
free_amount: Optional[Decimal]
```

Commission-free amount

### free\_currency instance-attribute

```python
free_currency: Optional[str]
```

Commission-free currency

### deductions\_status instance-attribute

```python
deductions_status: Type[DeductionStatus]
```

Deduction status

### deductions\_amount instance-attribute

```python
deductions_amount: Optional[Decimal]
```

Deduction amount

### deductions\_currency instance-attribute

```python
deductions_currency: Optional[str]
```

Deduction currency

### platform\_deducted\_status instance-attribute

```python
platform_deducted_status: Type[DeductionStatus]
```

Platform fee deduction status

### platform\_deducted\_amount instance-attribute

```python
platform_deducted_amount: Optional[Decimal]
```

Platform deduction amount

### platform\_deducted\_currency instance-attribute

```python
platform_deducted_currency: Optional[str]
```

Platform deduction currency

### history instance-attribute

```python
history: List[OrderHistoryDetail]
```

Order history details

### charge\_detail instance-attribute

```python
charge_detail: OrderChargeDetail
```

Order charges

## SubmitOrderResponse

Response for submit order request

### order\_id instance-attribute

```python
order_id: str
```

Order id

## CashInfo

CashInfo

### withdraw\_cash instance-attribute

```python
withdraw_cash: Decimal
```

Withdraw cash

### available\_cash instance-attribute

```python
available_cash: Decimal
```

Available cash

### frozen\_cash instance-attribute

```python
frozen_cash: Decimal
```

Frozen cash

### settling\_cash instance-attribute

```python
settling_cash: Decimal
```

Cash to be settled

### currency instance-attribute

```python
currency: str
```

Currency

## FrozenTransactionFee

### currency instance-attribute

```python
currency: str
```

Currency

### frozen\_transaction\_fee instance-attribute

```python
frozen_transaction_fee: Decimal
```

Frozen transaction fee

## AccountBalance

Account balance

### total\_cash instance-attribute

```python
total_cash: Decimal
```

Total cash

### max\_finance\_amount instance-attribute

```python
max_finance_amount: Decimal
```

Maximum financing amount

### remaining\_finance\_amount instance-attribute

```python
remaining_finance_amount: Decimal
```

Remaining financing amount

### risk\_level instance-attribute

```python
risk_level: int
```

Risk control level

### margin\_call instance-attribute

```python
margin_call: Decimal
```

Margin call

### currency instance-attribute

```python
currency: str
```

Currency

### cash\_infos instance-attribute

```python
cash_infos: List[CashInfo]
```

Cash details

### net\_assets instance-attribute

```python
net_assets: Decimal
```

Net assets

### init\_margin instance-attribute

```python
init_margin: Decimal
```

Initial margin

### maintenance\_margin instance-attribute

```python
maintenance_margin: Decimal
```

Maintenance margin

### buy\_power instance-attribute

```python
buy_power: Decimal
```

Buy power

### frozen\_transaction\_fees instance-attribute

```python
frozen_transaction_fees: FrozenTransactionFee
```

Frozen transaction fees

## BalanceType

### Unknown

Bases:

### Cash

Bases:

### Stock

Bases:

### Fund

Bases:

## CashFlowDirection

Cash flow direction

### Unknown

Bases:

Unknown

### Out

Bases:

Out

### In

Bases:

In

## CashFlow

Cash flow

### transaction\_flow\_name instance-attribute

```python
transaction_flow_name: str
```

Cash flow name

### direction instance-attribute

```python
direction: Type[CashFlowDirection]
```

Outflow direction

### business\_type instance-attribute

```python
business_type: Type[BalanceType]
```

Balance type

### balance instance-attribute

```python
balance: Decimal
```

Cash amount

### currency instance-attribute

```python
currency: str
```

Cash currency

### business\_time instance-attribute

```python
business_time: datetime
```

Business time

### symbol instance-attribute

```python
symbol: Optional[str]
```

Associated Stock code information

### description instance-attribute

```python
description: str
```

Cash flow description

## FundPosition

Fund position

### symbol instance-attribute

```python
symbol: str
```

Fund ISIN code

### current\_net\_asset\_value instance-attribute

```python
current_net_asset_value: Decimal
```

Current equity

### net\_asset\_value\_day instance-attribute

```python
net_asset_value_day: datetime
```

Current equity PyDecimal

### symbol\_name instance-attribute

```python
symbol_name: str
```

Fund name

### currency instance-attribute

```python
currency: str
```

Currency

### cost\_net\_asset\_value instance-attribute

```python
cost_net_asset_value: Decimal
```

Net cost

### holding\_units instance-attribute

```python
holding_units: Decimal
```

Holding units

## FundPositionChannel

Fund position channel

### account\_channel instance-attribute

```python
account_channel: str
```

Account type

### positions instance-attribute

```python
positions: List[FundPosition]
```

Fund positions

## FundPositionsResponse

Fund positions response

### channels instance-attribute

```python
channels: List[FundPositionChannel]
```

Channels

## StockPosition

Stock position

### symbol instance-attribute

```python
symbol: str
```

Stock code

### symbol\_name instance-attribute

```python
symbol_name: str
```

Stock name

### quantity instance-attribute

```python
quantity: Decimal
```

The number of holdings

### available\_quantity instance-attribute

```python
available_quantity: Decimal
```

Available quantity

### currency instance-attribute

```python
currency: str
```

Currency

### cost\_price instance-attribute

```python
cost_price: Decimal
```

Cost Price(According to the client's choice of average purchase or diluted cost)

### market instance-attribute

```python
market: Market
```

Market

### init\_quantity instance-attribute

```python
init_quantity: Optional[Decimal]
```

Initial position before market opening

## StockPositionChannel

Stock position channel

### account\_channel instance-attribute

```python
account_channel: str
```

Account type

### positions instance-attribute

```python
positions: List[StockPosition]
```

Stock positions

## StockPositionsResponse

Stock positions response

### channels instance-attribute

```python
channels: List[StockPositionChannel]
```

Channels

## TopicType

Topic type

### Private

Bases:

Private notification for trade

## MarginRatio

Margin ratio

### im\_factor instance-attribute

```python
im_factor: Decimal
```

Initial margin ratio

### mm\_factor instance-attribute

```python
mm_factor: Decimal
```

Maintain the initial margin ratio

### fm\_factor instance-attribute

```python
fm_factor: Decimal
```

Forced close-out margin ratio

## EstimateMaxPurchaseQuantityResponse

Response for estimate maximum purchase quantity

### cash\_max\_qty instance-attribute

```python
cash_max_qty: Decimal
```

Cash available quantity

### margin\_max\_qty instance-attribute

```python
margin_max_qty: Decimal
```

Margin available quantity

## TradeContext

Trade context

| Parameters: | - **`config`** () – 	Configuration object |
| --- | --- |

### \_\_init\_\_

```python
__init__(config: Config) -> None
```

### set\_on\_order\_changed

```python
set_on_order_changed(callback: Callable[[PushOrderChanged], None]) -> None
```

Set order changed callback, after receiving the order changed event, it will call back to this function.

### subscribe

```python
subscribe(topics: List[Type[TopicType]]) -> None
```

Subscribe

| Parameters: | - **`topics`** (`[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`) – 	Topic list |
| --- | --- |

Examples:

::

```python
from time import sleep
from decimal import Decimal
from longport.openapi import TradeContext, Config, OrderSide, OrderType, TimeInForceType, PushOrderChanged, TopicType

def on_order_changed(event: PushOrderChanged):
    print(event)

config = Config.from_env()
ctx = TradeContext(config)
ctx.set_on_order_changed(on_order_changed)
ctx.subscribe([TopicType.Private])

resp = ctx.submit_order(
    side = OrderSide.Buy,
    symbol = "700.HK",
    order_type = OrderType.LO,
    submitted_price = Decimal(50),
    submitted_quantity = Decimal(200),
    time_in_force = TimeInForceType.Day,
    remark = "Hello from Python SDK",
)
print(resp)
sleep(5)  # waiting for push event
```

### history\_executions

```python
history_executions(symbol: Optional[str] = None, start_at: Optional[datetime] = None, end_at: Optional[datetime] = None) -> List[Execution]
```

Get history executions

| Parameters: | - **`symbol`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by security code, example: `700.HK`, `AAPL.US` - **`start_at`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	Start time - **`end_at`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	End time |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Execution list |
| --- | --- |

Examples:

::

```python
from datetime import datetime
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.history_executions(
    symbol = "700.HK",
    start_at = datetime(2022, 5, 9),
    end_at = datetime(2022, 5, 12),
)
print(resp)
```

### today\_executions

```python
today_executions(symbol: Optional[str] = None, order_id: Optional[str] = None) -> List[Execution]
```

Get today executions

| Parameters: | - **`symbol`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by security code - **`order_id`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by Order ID |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Execution list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.today_executions(symbol = "700.HK")
print(resp)
```

### history\_orders

```python
history_orders(symbol: Optional[str] = None, status: Optional[List[Type[OrderStatus]]] = None, side: Optional[Type[OrderSide]] = None, market: Optional[Type[Market]] = None, start_at: Optional[datetime] = None, end_at: Optional[datetime] = None) -> List[Order]
```

Get history orders

| Parameters: | - **`symbol`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by security code - **`status`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by order status - **`side`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Filter by order side - **`market`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Filter by market type - **`start_at`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	Start time - **`end_at`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")]`, default: `None`) – 	End time |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Order list |
| --- | --- |

Examples:

::

```python
from datetime import datetime
from longport.openapi import TradeContext, Config, OrderStatus, OrderSide, Market

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.history_orders(
    symbol = "700.HK",
    status = [OrderStatus.Filled, OrderStatus.New],
    side = OrderSide.Buy,
    market = Market.HK,
    start_at = datetime(2022, 5, 9),
    end_at = datetime(2022, 5, 12),
)
print(resp)
```

### today\_orders

```python
today_orders(symbol: Optional[str] = None, status: Optional[List[Type[OrderStatus]]] = None, side: Optional[Type[OrderSide]] = None, market: Optional[Type[Market]] = None, order_id: Optional[str] = None) -> List[Order]
```

Get today orders

| Parameters: | - **`symbol`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by security code - **`status`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]]`, default: `None`) – 	Filter by order status - **`side`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Filter by order side - **`market`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Filter by market type - **`order_id`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Filter by order id |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Order list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config, OrderStatus, OrderSide, Market

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.today_orders(
    symbol = "700.HK",
    status = [OrderStatus.Filled, OrderStatus.New],
    side = OrderSide.Buy,
    market = Market.HK,
)
print(resp)
```

### replace\_order

```python
replace_order(order_id: str, quantity: Decimal, price: Optional[Decimal] = None, trigger_price: Optional[Decimal] = None, limit_offset: Optional[Decimal] = None, trailing_amount: Optional[Decimal] = None, trailing_percent: Optional[Decimal] = None, remark: Optional[str] = None) -> None
```

Replace order

| Parameters: | - **`quantity`** (`[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")`) – 	Replaced quantity - **`price`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Replaced price - **`trigger_price`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trigger price (`LIT` / `MIT` Order Required) - **`limit_offset`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Limit offset amount (`TSLPAMT` / `TSLPPCT` Required) - **`trailing_amount`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trailing amount (`TSLPAMT` / `TSMAMT` Required) - **`trailing_percent`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trailing percent (`TSLPPCT` / `TSMAPCT` Required) - **`remark`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Remark (Maximum 64 characters) |
| --- | --- |

Examples:

::

```sql
from decimal import Decimal
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

ctx.replace_order(
    order_id = "709043056541253632",
    quantity = Decimal(100),
    price = Decimal(100),
)
```

### submit\_order

```python
submit_order(symbol: str, order_type: Type[OrderType], side: Type[OrderSide], submitted_quantity: Decimal, time_in_force: Type[TimeInForceType], submitted_price: Optional[Decimal] = None, trigger_price: Optional[Decimal] = None, limit_offset: Optional[Decimal] = None, trailing_amount: Optional[Decimal] = None, trailing_percent: Optional[Decimal] = None, expire_date: Optional[date] = None, outside_rth: Optional[Type[OutsideRTH]] = None, remark: Optional[str] = None) -> SubmitOrderResponse
```

Submit order

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security code - **`order_type`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Order type - **`side`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Order Side - **`submitted_quantity`** (`[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")`) – 	Submitted quantity - **`time_in_force`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Time in force type - **`submitted_price`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Submitted price - **`trigger_price`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trigger price (`LIT` / `MIT` Required) - **`limit_offset`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Limit offset amount (`TSLPAMT` / `TSLPPCT` Required) - **`trailing_amount`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trailing amount (`TSLPAMT` / `TSMAMT` Required) - **`trailing_percent`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Trailing percent (`TSLPPCT` / `TSMAPCT` Required) - **`expire_date`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[date](https://docs.python.org/3/library/datetime.html#datetime.date "datetime.date")]`, default: `None`) – 	Long term order expire date (Required when `time_in_force` is `GoodTilDate`) - **`outside_rth`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Enable or disable outside regular trading hours - **`remark`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Remark (Maximum 64 characters) |
| --- | --- |

| Returns: | - – 	Response |
| --- | --- |

Examples:

::

```sql
from decimal import Decimal
from longport.openapi import TradeContext, Config, OrderSide, OrderType, TimeInForceType

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.submit_order(
    side = OrderSide.Buy,
    symbol = "700.HK",
    order_type = OrderType.LO,
    submitted_price = Decimal(50),
    submitted_quantity = Decimal(200),
    time_in_force = TimeInForceType.Day,
    remark = "Hello from Python SDK",
)
print(resp)
```

### cancel\_order

```python
cancel_order(order_id: str) -> None
```

Cancel order

| Parameters: | - **`order_id`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Order ID |
| --- | --- |

Examples:

::

```java
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

ctx.cancel_order("709043056541253632")
```

### account\_balance

```python
account_balance(currency: Optional[str] = None) -> List[AccountBalance]
```

Get account balance

| Parameters: | - **`currency`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Currency |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Account list |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.account_balance()
print(resp)
```

### cash\_flow

```python
cash_flow(start_at: datetime, end_at: datetime, business_type: Optional[Type[BalanceType]] = None, symbol: Optional[str] = None, page: Optional[int] = None, size: Optional[int] = None) -> List[CashFlow]
```

Get cash flow

| Parameters: | - **`start_at`** (`[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")`) – 	Start time - **`end_at`** (`[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "datetime.datetime")`) – 	End time - **`business_type`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]]`, default: `None`) – 	Balance type - **`symbol`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Target security code - **`page`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[int](https://docs.python.org/3/library/functions.html#int)]`, default: `None`) – 	Start page (Default: 1) - **`size`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[int](https://docs.python.org/3/library/functions.html#int)]`, default: `None`) – 	Page size (Default: 50) |
| --- | --- |

| Returns: | - `[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[]` – 	Cash flow list |
| --- | --- |

Examples:

::

```python
from datetime import datetime
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.cash_flow(
    start_at = datetime(2022, 5, 9),
    end_at = datetime(2022, 5, 12),
)
print(resp)
```

### fund\_positions

```python
fund_positions(symbols: Optional[List[str]] = None) -> FundPositionsResponse
```

Get fund positions

| Parameters: | - **`symbols`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]]`, default: `None`) – 	Filter by fund codes |
| --- | --- |

| Returns: | - – 	Fund positions |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.fund_positions()
print(resp)
```

### stock\_positions

```python
stock_positions(symbols: Optional[List[str]] = None) -> StockPositionsResponse
```

Get stock positions

| Parameters: | - **`symbols`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[List](https://docs.python.org/3/library/typing.html#typing.List "typing.List")[[str](https://docs.python.org/3/library/stdtypes.html#str)]]`, default: `None`) – 	Filter by stock codes |
| --- | --- |

| Returns: | - – 	Stock positions |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.stock_positions()
print(resp)
```

### margin\_ratio

```python
margin_ratio(symbol: str) -> MarginRatio
```

Get margin ratio

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security symbol |
| --- | --- |

| Returns: | - – 	Margin ratio |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.margin_ratio("700.HK")
print(resp)
```

### order\_detail

```python
order_detail(order_id: str) -> OrderDetail
```

Get order detail

| Parameters: | - **`order_id`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Order id |
| --- | --- |

| Returns: | - – 	Order detail |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.order_detail("701276261045858304")
print(resp)
```

### estimate\_max\_purchase\_quantity

```python
estimate_max_purchase_quantity(symbol: str, order_type: Type[OrderType], side: Type[OrderSide], price: Optional[Decimal] = None, currency: Optional[str] = None, order_id: Optional[str] = None, fractional_shares: bool = False) -> EstimateMaxPurchaseQuantityResponse
```

Estimating the maximum purchase quantity for Hong Kong and US stocks, warrants, and options

| Parameters: | - **`symbol`** (`[str](https://docs.python.org/3/library/stdtypes.html#str)`) – 	Security symbol - **`order_type`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Order type - **`side`** (`[Type](https://docs.python.org/3/library/typing.html#typing.Type "typing.Type")[]`) – 	Order side - **`price`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal "decimal.Decimal")]`, default: `None`) – 	Estimated order price, - **`currency`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Settlement currency - **`order_id`** (`[Optional](https://docs.python.org/3/library/typing.html#typing.Optional "typing.Optional")[[str](https://docs.python.org/3/library/stdtypes.html#str)]`, default: `None`) – 	Order ID, required when estimating the maximum purchase quantity for a modified order - **`fractional_shares`** (`[bool](https://docs.python.org/3/library/functions.html#bool)`, default: `False`) – |
| --- | --- |

| Returns: | - – 	Response |
| --- | --- |

Examples:

::

```lua
from longport.openapi import TradeContext, Config, OrderType, OrderSide

config = Config.from_env()
ctx = TradeContext(config)

resp = ctx.estimate_max_purchase_quantity(
    symbol = "700.HK",
    order_type = OrderType.LO,
    side = OrderSide.Buy,
)
print(resp)
```