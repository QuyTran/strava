import json
import hashlib
from stravalib import Client


class StravaModel:
    def __init__(self, my_strava_club_id, client_id, client_secret, host):
        self.my_strava_club_id = my_strava_club_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host

    def get_club_activities(self, start_event_id) -> list:
        access_token = self.get_strava_access_token()
        client = Client(access_token=access_token)
        data = []
        for athlete in client.get_club_activities(self.my_strava_club_id):
            formatted_row = self.to_array(athlete)
            if start_event_id == formatted_row[-1]:
                break
            data.append(formatted_row)
        return data

    def get_strava_access_token(self) -> str:
        f = open('access_token.json', )
        data = json.load(f)
        access_token = data['access_token']
        f.close()
        return access_token

    def to_array(self, activity_obj) -> list:
        obj = []
        obj.append(activity_obj.name)
        obj.append(str(activity_obj.start_date))
        obj.append(str(activity_obj.type))
        obj.append(float(str(activity_obj.distance).removesuffix(' m')))
        obj.append(str(activity_obj.moving_time))
        obj.append(str(activity_obj.elapsed_time))
        obj.append(str(activity_obj.total_elevation_gain).removesuffix('m'))
        obj.append(activity_obj.athlete.firstname + ' ' + activity_obj.athlete.lastname)
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
        with open('access_token.json', 'w') as f:
            f.write(json.dumps(access_token))

        return access_token