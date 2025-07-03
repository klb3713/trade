from backtrader.utils.py3 import with_metaclass
from backtrader.metabase import MetaParams
import collections

from longport.openapi import Config, QuoteContext, TradeContext

class MetaSingleton(MetaParams):
    '''Metaclass to make a metaclassed class a singleton'''
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = (
                super(MetaSingleton, cls).__call__(*args, **kwargs))
        return cls._singleton

class LongPortStore(with_metaclass(MetaSingleton, object)):
    '''LongPort Store for backtrader'''
    BrokerCls = None  # broker class will autoregister
    DataCls = None    # data class will auto register

    params = (
        # 可扩展参数，如 token、account 等
    )

    @classmethod
    def getdata(cls, *args, **kwargs):
        '''Returns DataCls with args, kwargs'''
        return cls.DataCls(*args, **kwargs)

    @classmethod
    def getbroker(cls, *args, **kwargs):
        '''Returns broker with *args, **kwargs from registered BrokerCls'''
        return cls.BrokerCls(*args, **kwargs)

    def __init__(self, **kwargs):
        super(LongPortStore, self).__init__()
        self.p = type('Params', (), kwargs)()  # 简单参数对象
        self.config = Config.from_env()
        self.quote_ctx = QuoteContext(self.config)
        self.trade_ctx = TradeContext(self.config)
        self.notifs = collections.deque()  # 通知队列
        self._env = None
        self.broker = None
        self.datas = list()

    def start(self, data=None, broker=None):
        if not self._started:
            self._started = True
            self.notifs = collections.deque()
            self.datas = list()
            self.broker = None

        if data is not None:
            self._cerebro = self._env = data._env
            self.datas.append(data)

            if self.broker is not None:
                if hasattr(self.broker, 'data_started'):
                    self.broker.data_started(data)

        elif broker is not None:
            self.broker = broker

    def stop(self):
        pass

    def put_notification(self, msg, *args, **kwargs):
        self.notifs.append((msg, args, kwargs))

    def get_notifications(self):
        '''Return the pending "store" notifications'''
        self.notifs.append(None)  # put a mark / threads could still append
        return [x for x in iter(self.notifs.popleft, None)]
