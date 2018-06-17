import pymysql
import time
import datetime
import MysqlDBManager

def calculate_rsi(graph_type, data_count):
    sum_of_up = 0 # 상승분 합
    sum_of_down = 0 # 하락분 합

    limit_rows = graph_type * data_count + 1
    query = "SELECT time_stamp, xrp FROM coin_info.coin_price ORDER BY time_stamp DESC LIMIT %d;" % limit_rows
    #mySqlDBManager = MySqlDBManager()
    rows = db_manager.select(query)

    for row_index in range(0,data_count):
        row_data = rows[row_index * graph_type]
        previous_row_data = rows[(row_index+1) * graph_type]
        delta_value = row_data[1] - previous_row_data[1]
        if delta_value > 0 :
            sum_of_up += delta_value
        else :
            sum_of_down += delta_value

    rsi = (sum_of_up / (sum_of_up - sum_of_down)) * 100

    currentTimeStamp = datetime.datetime.fromtimestamp((time.time() + 32400)).strftime('%Y-%m-%d %H:%M:%S')
    query = "insert into rsi values ('%s', '%s', '%d', '%d', '%f')" % (currentTimeStamp, "xrp", graph_type, data_count, rsi)
    db_manager.insert(query)
    return rsi

db_manager = MysqlDBManager.MySqlDBManager()
while True:
    try :
        rsi = calculate_rsi(10, 14)        
        print(rsi)        
    except Exception as exception :
        print(exception)
    finally :
        time.sleep(600)
