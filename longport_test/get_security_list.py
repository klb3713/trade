from longport.openapi import QuoteContext, Config, Market, SecurityListCategory

config = Config.from_env()
ctx = QuoteContext(config)
resp = ctx.security_list(Market.US, SecurityListCategory.Overnight)
print(resp)