import decideTrading
import MysqlDBManager
import datetime
from Slack import send_message_to_slack
import time
import CoinOneApi 
from MyException import getTracebackStr
from threading import Timer

def check_previous_order_status(order_id, coin_type):
	try :

		order_information = CoinOneApi.get_order_information(order_id, coin_type)

		if order_information["errorCode"] != '0' :
			print("COIN_ONE API Response_Error, ErrorCode :", order_information["errorCode"])
		else :
			time_stamp = order_information["info"]["timestamp"]
			order_quantity = double(order_information["info"]["qty"])
			trade_type = order_information["info"]["type"]
			fee = order_information["info"]["fee"]
			order_price = order_information["info"]["price"]
			remain_quantity = double(order_information["info"]["remainQty"])
			order_status = order_information["status"]

			message = ("Prev_Order[{0}] is {1}").format(order_id, order_status)
			send_message_to_slack(message)

			if order_status != "live":
				sql = ( "insert into complete_order_info('order_id', 'time_stamp', 'coin_type', 'trade_type', 'order_status', 'complete_price', 'complete_quantity', 'fee') "
					    "values ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})"
					  ).format(order_id, time_stamp, coin_type, trade_type, order_status, order_price, order_quantity - remain_quantity, fee)

	except Exception as e:
		print(getTracebackStr())
		send_message_to_slack('Exception \n'+ str( getTracebackStr() ) )

def reorder_live_sell_order(order_id, coin_type):
	try :

		order_information = CoinOneApi.get_order_information(order_id, coin_type)

		if order_information["errorCode"] != '0' :
			print("COIN_ONE API Response_Error, ErrorCode :", order_information["errorCode"])
		else :
			time_stamp = order_information["info"]["timestamp"]
			order_quantity = double(order_information["info"]["qty"])
			trade_type = order_information["info"]["type"]
			fee = order_information["info"]["fee"]
			order_price = order_information["info"]["price"]
			remain_quantity = double(order_information["info"]["remainQty"])
			order_status = order_information["status"]

			message = ("Prev_Order[{0}] is {1}").format(order_id, order_status)
			send_message_to_slack(message)

			if order_status != "live":
				sql = ( "insert into complete_order_info('order_id', 'time_stamp', 'coin_type', 'trade_type', 'order_status', 'complete_price', 'complete_quantity', 'fee') "
					    "values ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})"
					  ).format(order_id, time_stamp, coin_type, trade_type, order_status, order_price, order_quantity - remain_quantity, fee)

			if order_status != "filled":
				cancel_result = CoinOneApi.cancel_order(order_id, order_price, remain_quantity, coin_type, 1)

				if cancel_result["errorCode"] == '0' :
					sql = ( "select {0} "
							"FROM coin_price "
							"order by time_stamp desc limit 1"
						).format(coin_type)

					row = db_manager.select(sql)
					order_price = row[0][0]

					current_time = datetime.datetime.now() + datetime.timedelta(hours=9)

					trading_data = []
					trading_data.append(current_time)
					trading_data.append(decideTrading.TradeDecision.SELL)
					trading_data.append(-1)
					trading_data.append(-1)

					order_info = order_sell(trading_data, coin_type, order_price)

					event = Timer(60, reorder_live_sell_order, [order_info["orderId"], coin_type])
					event.start()
				else :
					print("COIN_ONE API Response_Error, ErrorCode :", cancel_result["errorCode"])

	except Exception as e:
		print(getTracebackStr())
		send_message_to_slack('Exception \n'+ str( getTracebackStr() ) )



def order_buy(decide_trading_data, coin_type, order_price):
	# 매수
	message = ''
	return_value = False
	
	if CoinOneApi.get_avail_account('krw') > 1000:
		avail_account_krw = CoinOneApi.get_avail_account('krw')
		order_quantity = round(avail_account_krw/order_price,4)-0.0001
		
		order_data = {
			'price': order_price,
			'qty': order_quantity,
			'currency': coin_type
		}

		return_value = CoinOneApi.order_coin('buy',order_data)
	else:
		message = ' krw lack of available balance'
		return_value = False
	
	if return_value != False:
		current_time_stamp = decide_trading_data[0]
		trade_type = decide_trading_data[1]
		current_rsi = decide_trading_data[2]
		previous_rsi = decide_trading_data[3]
		
		sql = ( "insert into order_status_log (order_id, time_stamp, coin_type, trade_type, order_price, order_quantity, current_rsi, previous_rsi)"
			"values ('%s','%s','%s','%s','%f','%f','%f', '%f')" 
			% (return_value["orderId"], current_time_stamp, coin_type, trade_type, order_price, order_quantity, current_rsi, previous_rsi)
		)
		
		db_manager.insert(sql)

		message = ("Buy {0} Price : {1} Quantity : {2} ID : {3}").format(coin_type, order_price, order_quantity, return_value["orderId"])

	send_message_to_slack(message)

	return return_value

def order_sell(decide_trading_data, coin_type, order_price):
	# 매수
	message = ''
	return_value = False
	
	if CoinOneApi.get_avail_account(coin_type) >= 1:
		avail_account_coin = CoinOneApi.get_avail_account(coin_type)
		order_quantity = round(avail_account_coin, 4) - 0.0001
		
		order_data = {
			'price': order_price,
			'qty': order_quantity,
			'currency': coin_type
		}
		
		return_value = CoinOneApi.order_coin('sell',order_data)
	else:
		message = coin_type + ' lack of available balance'
		return_value = False		
	
	if return_value != False:
		current_time_stamp = decide_trading_data[0]
		trade_type = decide_trading_data[1]
		current_rsi = decide_trading_data[2]
		previous_rsi = decide_trading_data[3]
		
		sql = ( "insert into order_status_log (order_id, time_stamp, coin_type, trade_type, order_price, order_quantity, current_rsi, previous_rsi)"
			"values ('%s','%s','%s','%s','%f','%f','%f', '%f')" 
			% (return_value["orderId"], current_time_stamp, coin_type, trade_type, order_price, order_quantity, current_rsi, previous_rsi)
		)
		
		db_manager.insert(sql)

		message = ("Sell {0} Price : {1} Quantity : {2} ID : {3}").format(coin_type, order_price, order_quantity, return_value["orderId"])

	send_message_to_slack(message)

	return return_value

db_manager = MysqlDBManager.MySqlDBManager()
coin_type = 'xrp'
while True : 
	try:
		current_time = datetime.datetime.now() + datetime.timedelta(hours=9)
		decide_trading_data = decideTrading.decide_trade_by_rsi(current_time, coin_type)
		trade_decision = decide_trading_data[1]
		current_time_stamp = decide_trading_data[0]
		
		if trade_decision != decideTrading.TradeDecision.STAY :
			sql = ( "select {0} "
					"FROM coin_price "
					"WHERE Date_format('{1}','%Y-%m-%d %H:%i') >= Date_format(time_stamp,'%Y-%m-%d %H:%i') "
					"order by time_stamp desc limit 1"
			).format(coin_type, current_time_stamp)

			row = db_manager.select(sql)
			order_price = row[0][0]

			if trade_decision == decideTrading.TradeDecision.BUY :
				order_info = order_buy(decide_trading_data, coin_type, order_price)
				if order_info != False:
					event = Timer(60, check_previous_order_status, [order_info["orderId"], coin_type])
					event.start()
			elif trade_decision == decideTrading.TradeDecision.SELL or trade_decision == decideTrading.TradeDecision.LOSS_CUT:
				order_info = order_sell(decide_trading_data, coin_type, order_price)
				if order_info != False:
					event = Timer(60, reorder_live_sell_order, [order_info["orderId"], coin_type])
					event.start()

			print(trade_decision, ' ', coin_type)

	except Exception as e:
		print(getTracebackStr())
		send_message_to_slack('Exception \n'+ str( getTracebackStr() ) )
	finally:
		time.sleep(600)
