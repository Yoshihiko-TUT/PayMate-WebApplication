from datetime import datetime as dt
from datetime import timedelta
import googleapiclient.discovery
import google.auth
import pickle

class PayMate:
    def __init__(self, c_id):
        # Google APIの準備をする
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.calendar_id = c_id
        # Googleの認証情報をファイルから読み込む
        gapi_creds = google.auth.load_credentials_from_file('setup.json', SCOPES)[0]
        # APIと対話するためのResourceオブジェクトを構築する
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds, static_discovery=False)

        # バイナリファイルからデータをロード
        with open('data.bin', 'rb') as f:
            self.paydays, self.pay_period = pickle.load(f)

    def calculate(self, salary):
        output = []
        # 各月ごとに計算・出力
        for index, date in enumerate(self.pay_period):
            start_date = date[0].strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            end_date = (date[1] + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            total = 0

            # イベントの取得
            events_result = self.service.events().list(calendarId=self.calendar_id, timeMin=start_date, timeMax=end_date,
                                                maxResults=1000, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items')
            # 全てのイベントを
            for event in events:
                event_name = event.get('summary')
                if event_name in salary.keys():
                    start_time = dt.fromisoformat(event.get('start').get('dateTime'))
                    end_time = dt.fromisoformat(event.get('end').get('dateTime'))

                    duration = (end_time - start_time).total_seconds() / 3600
                    if event_name == 'TA' and duration > (10/6):
                        duration -= 0.25 * (duration // (10/6) - 1)
                    total += salary[event_name] * duration

            output.append(f"{self.paydays[index].date()}の支給額は ¥{'{:,}'.format(int(total))}")
        return output
    
if __name__ == "__main__":
    pm = PayMate()
    # それぞれの表記と給料
    salary = {'TA':2334, 'TA MT':2334, '学修支援センター':2500, '学修支援センター MT':2500}
    out = pm.calculate(salary)
    for t in out:
        print(t)