import json
import hashlib
import time
from datetime import date

from stravalib import Client


class StravaModel:
    def __init__(self, my_strava_club_id, client_id, client_secret, host):
        self.my_strava_club_id = my_strava_club_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host

    def get_club_activities(self, start_event_id) -> dict:
        access_token = self.get_strava_access_token()
        access_token = self.refresh_access_token(access_token)
        client = Client(access_token=access_token['access_token'])
        data = {}
        for athlete in client.get_club_activities(self.my_strava_club_id):
            formatted_row = self.to_array(athlete)
            if start_event_id == formatted_row[-1]:
                print('found!')
                break
            data[formatted_row[-1]] = formatted_row
        return data

    def refresh_access_token(self, access_token) -> list:
        if access_token['expires_at'] < time.time():
            client = Client(access_token=access_token['access_token'])
            new_access_token = client.refresh_access_token(self.client_id,
                                                           self.client_secret,
                                                           access_token['refresh_token'])
            self.write_access_token_to_file(new_access_token)
            return new_access_token

        return access_token

    def get_strava_access_token(self) -> list:
        f = open('access_token.json', )
        data = json.load(f)
        f.close()
        return data

    def to_array(self, activity_obj) -> list:
        now = date.today()
        obj = []
        obj.append(activity_obj.name)
        obj.append(str(activity_obj.start_date))
        obj.append(str(activity_obj.type))
        obj.append(float(str(activity_obj.distance).removesuffix(' m')))
        obj.append(str(activity_obj.moving_time))
        obj.append(str(activity_obj.elapsed_time))
        obj.append(str(activity_obj.total_elevation_gain).removesuffix('m'))
        obj.append(activity_obj.athlete.firstname + ' ' + activity_obj.athlete.lastname)
        obj.append(now.strftime("%Y/%m/%d"))
        event_id = hashlib.md5(json.dumps(obj, sort_keys=True).encode('utf-8')).hexdigest()
        obj.append(event_id)
        user_id = hashlib.md5(
            json.dumps([activity_obj.athlete.firstname, activity_obj.athlete.lastname], sort_keys=False).encode(
                'utf-8')).hexdigest()
        obj.insert(0, user_id)
        return obj

    def get_auth_url(self) -> str:
        client = Client()
        return client.authorization_url(client_id=self.client_id,
                                        redirect_uri=self.host + 'authorization',
                                        approval_prompt='auto',
                                        scope=['read_all', 'profile:read_all', 'activity:read_all', 'activity:write']
                                        )

    def save_access_token(self, code) -> str:
        client = Client()
        access_token = client.exchange_code_for_token(client_id=self.client_id,
                                                      client_secret=self.client_secret,
                                                      code=code)
        self.write_access_token_to_file(access_token)
        return access_token

    def write_access_token_to_file(self, access_token):
        with open('access_token.json', 'w') as f:
            f.write(json.dumps(access_token))
