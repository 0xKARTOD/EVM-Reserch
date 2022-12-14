from datetime import timedelta
import pandas as pd

def last_month_addresses(data):
    last_date = (max(data['Date(UTC)']))

    data_last_month_avg = (data[data['Date(UTC)'].between((last_date - timedelta(days = 30)), last_date)]).groupby('CHAIN').mean()
    data_last_month_avg['CHAIN'] = data_last_month_avg.index.get_level_values(0)
    data_last_month_avg = data_last_month_avg.reset_index(drop=True)

    return data_last_month_avg, last_date


def table_data(data):
    data_last_month_avg, last_date = last_month_addresses(data)

    _table_data = data[data['Date(UTC)'] == last_date].merge(data_last_month_avg, on='CHAIN', how='inner', suffixes=('_1', '_2'))

    _table_data['Pct txs'] = 100*(_table_data['Value_1'] - _table_data['Value_2'])/_table_data['Value_2']
    _table_data['Pct addresses'] = 100*(_table_data['Active addresses_1'] - _table_data['Active addresses_2'])/_table_data['Active addresses_2']
    _table_data['Pct time'] = -100*(_table_data['Block time_1'] - _table_data['Block time_2'])/_table_data['Block time_1']
    _table_data['Pct blocks'] = 100*(_table_data['Blocks count_1'] - _table_data['Blocks count_2'])/_table_data['Blocks count_1']


    _table_data_result  = pd.DataFrame()
    _table_data_result['CHAIN'] = _table_data['CHAIN']
    _table_data_result = _table_data_result.merge(data_last_month_avg, on='CHAIN', how='left')

    _table_data_result['# of Transactions'] = [
        str("{:,.2f}".format(_table_data['Value_1'][v])) + 
        " (" +
        str(round(_table_data['Pct txs'][v], 2)) + 
        "%)"
        for v in range(len(_table_data['Value_1']))]

    _table_data_result['# of Active addresses'] = [
        str("{:,.2f}".format(_table_data['Active addresses_1'][v])) + 
        " (" +
        str(round(_table_data['Pct addresses'][v], 2)) + 
        "%)"
        for v in range(len(_table_data['Active addresses_1']))]

    _table_data_result['Block time [s]'] = [
        str("{:,.2f}".format(round(_table_data['Block time_1'][v], 1))) + 
        " (" +
        str(round(_table_data['Pct time'][v], 2)) + 
        "%)"
        for v in range(len(_table_data['Block time_1']))]

    _table_data_result['# of Blocks'] = [
        str("{:,.2f}".format(_table_data['Blocks count_1'][v])) + 
        " (" +
        str(round(_table_data['Pct blocks'][v], 2)) + 
        "%)"
        for v in range(len(_table_data['Blocks count_1']))]
    
    _table_data_result['Pct txs'] = _table_data['Pct txs']
    _table_data_result['Pct addresses'] = _table_data['Pct addresses']
    _table_data_result['Pct time'] = _table_data['Pct time']
    _table_data_result['Pct blocks'] = _table_data['Pct blocks']
    
    return _table_data_result, last_date