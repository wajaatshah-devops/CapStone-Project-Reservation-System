from datetime import datetime, date, timedelta

def formatDate(date):
    dateStr = date[6:11] + '-' + date[0:2] + '-' + date[3:5]
    return (dateStr)

today = '01-01-2021'

today = formatDate(today)
print(today)

todayDate = date.today()
todayDateStr = date.today().strftime('%Y-%m-%d')

if today < todayDateStr:
    print ('today is lesss than todayDate')
else:
    print('Today greater than todayDate')