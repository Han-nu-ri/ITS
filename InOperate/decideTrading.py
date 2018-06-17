#1. RSI 코드 구현 (정피창, 이광철)
#   +) 사고팔고 이득/손해 시뮬레이셔닝
#   step
#   1. 10분봉 RSI(14) Data 가져오기
#   2. ↗50(50 초과), ↘50(50 미만), ↘80(80 미만), ↘70(70 미만) 판단(How?? : )
#   3. BUY(살것), SELL(팔것), STAY(아무것도 안할 것)

import pymysql
from enum import Enum

class TradeDecision(Enum):
   BUY = 1
   SELL = 2
   STAY = 3
   LOSS_CUT = 4

# get_rsi_data : RSI Data를 가져오는 함수
# graph_type : 3, 5, 7, 10봉
# rsi_type : rsi9, rsi14
# coin_type : coin 종류
# rsi_data_count : 가져올 rsi Data 갯수
def get_rsi_data(time_stamp, graph_type, rsi_type, coin_type, rsi_data_count):

   connection = pymysql.connect(host = 'localhost', user = 'root', password = 'root', db = 'coin_info')
   cursor = connection.cursor()
   
   sql = "SELECT time_stamp, value FROM coin_info.rsi WHERE coin_type='{0}' and graph_type={1} and rsi_type={2} and time_stamp <= '{3}' ORDER BY time_stamp DESC LIMIT {4};".format(coin_type, graph_type, rsi_type, time_stamp, rsi_data_count)

   cursor.execute(sql)
   rows = cursor.fetchall()
   connection.close()

   return rows

# decide_trade : rsi에 의해 해당 coin을 사고 팔지 결정하는 로직
# coin_type : coin 종류
def decide_trade_by_rsi(time_stamp, coin_type):
   return_val = []
   graph_type = 10
   rsi_type = 14
   rsi_data_count = 2
   
   rsi_data_array = get_rsi_data(time_stamp, graph_type, rsi_type, coin_type, rsi_data_count)
   
   previous_rsi_value = rsi_data_array[1][1]
   current_rsi_value = rsi_data_array[0][1]
   current_time_stamp = rsi_data_array[0][0]
   return_val.append(current_time_stamp)

   if (current_rsi_value > 30 and previous_rsi_value <= 30 ):#and current_rsi_value - previous_rsi_value > 7.5):
      return_val.append(TradeDecision.BUY)
   elif (current_rsi_value < 70 and previous_rsi_value >= 70 ):#and previous_rsi_value - current_rsi_value > 7.5):
      return_val.append(TradeDecision.SELL)
   elif (current_rsi_value <= 20 ) :
      return_val.append(TradeDecision.LOSS_CUT)
   else:
      return_val.append(TradeDecision.STAY)

   return_val.append(current_rsi_value)
   return_val.append(previous_rsi_value)

   return return_val
