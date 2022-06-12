# Cr. Meawbin Investor
import ccxt

def authen(apiKey, secret, password, accountName):

    exchange = ccxt.ftx({
        'apiKey' : apiKey ,
        'secret' : secret ,
        'password' : password ,
        'enableRateLimit': True
        })
    if accountName == "" :
        print("\n""Account Name - This is Main Account",': Broker - ',exchange)     
    else:
        print( "\n"'Account Name - ',accountName,': Broker - ',exchange)
        exchange.headers = {'ftx-SUBACCOUNT': accountName,}
    return exchange

def fetchBalance(client, asset_1, asset_2, quote):
    balances = client.fetch_balance()
    ticker = client.fetch_ticker(quote)
    asset_1_val, asset_2_val = balances.get(asset_1, {}).get("total", None), \
        balances.get(asset_2, {}).get("total", None)
    print("asset_1_val:", asset_1_val)
    print("asset_2_val:", asset_2_val)
    
    if asset_1_val is None or asset_2_val is None:
        raise ValueError("No balance available for trading")
   
    averagePrice = (ticker["bid"] + ticker["ask"]) / 2
    return asset_1_val, asset_2_val, averagePrice

def action(asset_1_val: float, asset_2_val: float, averagePrice: float, client, quote, pcdiff):

    asset_1_crrt_val = asset_1_val * averagePrice
    asset_2_crrt_val = asset_2_val * 1
    rebalance_mark   = ((asset_1_crrt_val + asset_2_crrt_val) / 2)
    rebalance_percent_diff = pcdiff

    if   asset_1_crrt_val > (rebalance_mark + (rebalance_mark*rebalance_percent_diff/100) ) :
        print("asset_1_crrt_val ",asset_1_crrt_val ,">", (rebalance_mark + (rebalance_mark*rebalance_percent_diff/100) ))
        print("SELL")
        diff_sell  = asset_1_crrt_val - rebalance_mark
        print(diff_sell)
        client.create_order(quote ,'market','sell',(diff_sell / averagePrice)) # Unit USD/Price
        return True, "profit"
    elif asset_1_crrt_val < (rebalance_mark - (rebalance_mark*rebalance_percent_diff/100) ) :
        print("asset_1_crrt_val ",asset_1_crrt_val ,"<", (rebalance_mark - (rebalance_mark*rebalance_percent_diff/100) ))
        print("Buy")
        diff_buy  = rebalance_mark - asset_1_crrt_val
        print(diff_buy)
        client.create_order(quote ,'market','buy',(diff_buy / averagePrice))
        return True, "loss"
    else :
        print("None Trade")
        return False, ""

def main():
    #load env
    from dotenv import load_dotenv
    import os
    import time
    from datetime import datetime

    load_dotenv()
    apiKey = os.getenv("APIKEY")
    secret = os.getenv("SECRET")
    password = os.getenv("PASSWORD")
    accountName = os.getenv("ACCOUNT_NAME")
    asset_1 = os.getenv("ASSET_1")
    asset_2 = os.getenv("ASSET_2")
    percent_1 = os.getenv("PERCENT_1")
    percent_2 = os.getenv("PERCENT_2")
    interval = int(os.getenv("INTERVALSEC"))
    pcdiff = float(os.getenv("PCDIFF"))

    # make param
    quote = str(asset_1) + "/" + str(asset_2)

    if asset_2 != "USD":
        raise(NotImplementedError("Only supported Coin-USD"))

    client = authen(apiKey, secret, password, accountName)
    while True:
        print(datetime.now())
        print(f"Coin/USD: {asset_1}/{asset_2}")
        try:
            asset_1_val, asset_2_val, averagePrice = fetchBalance(
                client, asset_1, asset_2, quote)
            action(asset_1_val, asset_2_val, averagePrice, client, quote, pcdiff)
            time.sleep(interval)
        except:
            time.sleep(interval)
    
if __name__ == "__main__":
    main()