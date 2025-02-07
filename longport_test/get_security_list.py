from longport.openapi import QuoteContext, Config, Market, SecurityListCategory
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("stocks_list")
# 初始化log
logger.setLevel(logging.INFO)

# 创建一个handler，用于写入日志文件，每天一个文件，保留30天
log_path = os.path.join("",'stocks_list.log')
handler = TimedRotatingFileHandler(log_path, when='D', interval=1, backupCount=30)
handler.setLevel(logging.INFO)

# 创建一个输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 添加handler到logger
logger.addHandler(handler)

logger.info('Started')

config = Config(
            app_key="fddd1f64ad477d0aea79928c749cc581",
            app_secret="d7873d6e17dbff6c0f1bb6ccf3f5a638f044ee9b6ba7f87e92399c8e8164357e",
            access_token="m_eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb25nYnJpZGdlIiwic3ViIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzQyOTk4MzQ3LCJpYXQiOjE3MzUyMjIzNDMsImFrIjoiZmRkZDFmNjRhZDQ3N2QwYWVhNzk5MjhjNzQ5Y2M1ODEiLCJhYWlkIjoyMDUxMzYxNywiYWMiOiJsYl9wYXBlcnRyYWRpbmciLCJtaWQiOjEzNzY5MjY3LCJzaWQiOiJ1N1Fxak51RWd2ZzEydzhMNkR2WmF3PT0iLCJibCI6MywidWwiOjAsImlrIjoibGJfcGFwZXJ0cmFkaW5nXzIwNTEzNjE3In0.X3C9g7KJ8F_gjyRT5EOtC1q-b6pmTGHe9_vFHz8KwKuZSIPSC7elUdyprOlWNNfKLOS5_xFhIwDCDo62WHq0KRyTqUOELfPphSMiqkk5H9nICGNJ7Oi7vzuqppuj-kZNjTerY-h1G45l68GV6Uv0VpIuukRRQ9tziteG42GweV5UKp4qGJkQYK682ORptSlXNyhnMAOry-heuubpwtmrlh-J2U-NnbiKyuvEM_U9S2NkemF_AmirZ_hGPmJSjMRhrcoAavWrO4zMIKDSFE4zKn7R4h8ow32yWpaRQVIJU_NDto-lwAshytGq0TiE5EgEU_iizzvClaASfhgSUWht6sNhj5A4UHkIcB2-S5uMHLgkaIE-Zuvy1iglN-WpEFgTllR4HqEG2G_Vt9JqLGkCRNwYoOkyYIbQkbGIbx8dVivp12N0S5GOkCcedokKL-0SbuJ2HTD-How-mPRhUGeeSwJWQyXYHTOGy4X2j60J7R8koUMGATCLxWRnU94wbVDUe3yRfYqEYmWEmM8gQkOyZC2ozWcu0zysyjLVp4stCApl1c9XiDODdQFhBgUo_MFvKMG82X826EFfYkudW4zsgRsrHj5IIz5qWj0qzkiY1BOtDfMRwkyPi_gsagUaTsSk0RrKBEvOtZXKZvWHfDO5HXsC-NQ63wVb4nTBNH-mMmk",
            enable_overnight=True)
ctx = QuoteContext(config)
resp = ctx.security_list(Market.US, SecurityListCategory.Overnight)
logger.info(resp) 