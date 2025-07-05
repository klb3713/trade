#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# LongPortBroker for backtrader
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import threading
import time
from decimal import Decimal

from backtrader.broker import BrokerBase
from backtrader.comminfo import CommInfoBase
from backtrader.position import Position
from backtrader.utils.py3 import queue, with_metaclass

# 依赖 longport-openapi 官方 SDK
from longport.openapi import TradeContext, Config, OrderSide, OrderType, TimeInForceType, PushOrderChanged, OrderStatus, TopicType
from backtrader.order import BuyOrder, SellOrder, Order
from longport_bt import longportstore 


class MetaLongPortBroker(BrokerBase.__class__):
    def __init__(cls, name, bases, dct):
        '''Class has already been created ... register'''
        # Initialize the class
        super(MetaLongPortBroker, cls).__init__(name, bases, dct)
        longportstore.LongPortStore.BrokerCls = cls


class LongPortBroker(with_metaclass(MetaLongPortBroker, BrokerBase)):
    params = (
        ('commission', CommInfoBase(percabs=True)),
    )

    _store = longportstore.LongPortStore
    
    def __init__(self, **kwargs):
        super(LongPortBroker, self).__init__()
        self.lp = self._store(**kwargs)
        self.ctx = self.lp.trade_ctx
        self.startingcash = 0.0
        self._cash = 0.0
        self._value = 0.0
        self._positions = dict()  # symbol -> Position
        self._orders = dict()     # order_id -> order
        self.notifs = queue.Queue()
        self._lock = threading.Lock()
        self._order_status_map = {}  # order_id -> last status
        self._order_ref_map = {}     # 本地 order.ref -> order
        self._order_id_to_ref = {}   # longport order_id -> order.ref
        self._userhist = []          # 历史订单导入


    def start(self):
        super(LongPortBroker, self).start()
        self._update_account()
        self._update_positions()
        self.startingcash = self._cash
        self.ctx.set_on_order_changed(self._on_order_changed)
        self.ctx.subscribe([TopicType.Private])

    def stop(self):
        super(LongPortBroker, self).stop()
        self.ctx.unsubscribe([TopicType.Private])
        pass

    def _update_account(self):
        balances = self.ctx.account_balance()
        if balances:
            self._cash = float(balances[0].total_cash)
            self._value = float(balances[0].net_assets)
        else:
            self._cash = 0.0
            self._value = 0.0

    def _update_positions(self):
        self._positions.clear()
        resp = self.ctx.stock_positions()
        if resp.channels:
            for pos in resp.channels[0].positions:
                self._positions[pos.symbol] = Position(size=float(pos.quantity), price=float(pos.cost_price))

    def getcash(self):
        return self._cash

    def getvalue(self, datas=None):
        return self._value

    def getposition(self, data):
        symbol = getattr(data, 'symbol', None) or getattr(data, '_name', None)
        pos = self._positions.get(symbol)
        if pos:
            return pos
        return Position(size=0.0, price=0.0)

    def _map_exectype(self, exectype, order=None):
        from backtrader.order import Order
        if exectype is None or exectype == Order.Market:
            return OrderType.MO, {}
        elif exectype == Order.Limit:
            return OrderType.LO, {}
        elif exectype == Order.Stop:
            return OrderType.MIT, {'trigger_price': Decimal(str(order.price)) if order else None}
        elif exectype == Order.StopLimit:
            return OrderType.LIT, {
                'trigger_price': Decimal(str(order.price)) if order else None,
                'submitted_price': Decimal(str(order.pricelimit)) if order else None
            }
        elif exectype == Order.StopTrail:
            return OrderType.TSMAMT, {
                'trailing_amount': Decimal(str(order.trailamount)) if order and order.trailamount else None,
                'trailing_percent': Decimal(str(order.trailpercent)) if order and order.trailpercent else None
            }
        elif exectype == Order.StopTrailLimit:
            return OrderType.TSLPAMT, {
                'trailing_amount': Decimal(str(order.trailamount)) if order and order.trailamount else None,
                'trailing_percent': Decimal(str(order.trailpercent)) if order and order.trailpercent else None,
                'limit_offset': Decimal(str(order.pricelimit)) if order and order.pricelimit else None
            }
        else:
            return OrderType.MO, {}

    def submit(self, order):
        symbol = getattr(order.data, 'symbol', None) or getattr(order.data, '_name', None)
        side = OrderSide.Buy if order.isbuy() else OrderSide.Sell
        order_type, extra = self._map_exectype(order.exectype, order)
        price = Decimal(str(order.price)) if hasattr(order, 'price') and order.price is not None else None
        quantity = Decimal(str(abs(order.size)))
        tif = TimeInForceType.Day
        kwargs = {
            'symbol': symbol,
            'order_type': order_type,
            'side': side,
            'submitted_quantity': quantity,
            'time_in_force': tif,
        }
        if price is not None and order_type in [OrderType.LO, OrderType.LIT]:
            kwargs['submitted_price'] = price
        kwargs.update({k: v for k, v in extra.items() if v is not None})
        try:
            resp = self.ctx.submit_order(**kwargs)
            time.sleep(50)
            order.order_id = resp.order_id
            self._orders[resp.order_id] = order
            self._order_id_to_ref[resp.order_id] = order.ref
            self._order_ref_map[order.ref] = order
            order.submit(self)
            self.notifs.put(order)
            return order
        except Exception as e:
            order.info['error'] = str(e)
            self.notifs.put(order)
            return order

    def buy(self, owner, data, size, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0, oco=None,
            trailamount=None, trailpercent=None, **kwargs):
        order = BuyOrder(owner=owner, data=data,
                         size=size, price=price, pricelimit=plimit,
                         exectype=exectype, valid=valid, tradeid=tradeid,
                         trailamount=trailamount, trailpercent=trailpercent)
        order.addinfo(**kwargs)
        return self.submit(order)

    def sell(self, owner, data, size, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0, oco=None,
             trailamount=None, trailpercent=None, **kwargs):
        order = SellOrder(owner=owner, data=data,
                          size=size, price=price, pricelimit=plimit,
                          exectype=exectype, valid=valid, tradeid=tradeid,
                          trailamount=trailamount, trailpercent=trailpercent)
        order.addinfo(**kwargs)
        return self.submit(order)

    def cancel(self, order):
        order_id = getattr(order, 'order_id', None)
        if order_id:
            try:
                self.ctx.cancel_order(order_id)
                order.cancel()
                self.notifs.put(order)
            except Exception as e:
                order.info['error'] = str(e)
                self.notifs.put(order)

    def next(self):
        self.notifs.put(None)

    def get_notification(self):
        try:
            return self.notifs.get(False)
        except queue.Empty:
            pass
        return None

    def getcommissioninfo(self, data):
        return self.p.commission

    def _on_order_changed(self, event: PushOrderChanged):
        print("_on_order_changed")
        order_id = event.order_id
        status = event.status
        order = self._orders.get(order_id)
        if order is None:
            return
        # 保存原始事件
        order.info['longport_event'] = event
        # 状态流转
        if status == OrderStatus.New:
            order.accept(self)
        elif status == OrderStatus.Filled:
            # 成交明细
            exec_qty = float(event.executed_quantity or 0)
            exec_price = float(event.executed_price or 0)
            # 资金、持仓同步
            self._update_account()
            self._update_positions()
            # 调用 execute
            order.execute(event.updated_at, exec_qty, exec_price,
                          exec_qty, exec_qty * exec_price, 0.0,  # closed, closedvalue, closedcomm
                          0.0, 0.0, 0.0,  # opened, openedvalue, openedcomm
                          0.0, 0.0,  # margin, pnl
                          exec_qty, exec_price)
            order.completed()
        elif status == OrderStatus.PartialFilled:
            exec_qty = float(event.executed_quantity or 0)
            exec_price = float(event.executed_price or 0)
            self._update_account()
            self._update_positions()
            order.execute(event.updated_at, exec_qty, exec_price,
                          exec_qty, exec_qty * exec_price, 0.0,
                          0.0, 0.0, 0.0,
                          0.0, 0.0,
                          exec_qty, exec_price)
            order.partial()
        elif status == OrderStatus.Canceled:
            order.cancel()
        elif status == OrderStatus.Rejected:
            order.reject()
        self.notifs.put(order)

    def add_order_history(self, orders, notify=True):
        # orders: [(dt, size, price, data_name), ...]
        for o in orders:
            dt, size, price, data_name = o
            # 这里只导入历史，不下单
            self._userhist.append([dt, size, price, data_name]) 