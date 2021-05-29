from flask import Flask, jsonify, request, abort
from flask import render_template
import click
import json
import os
from stravalib import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import googleapiclient
from googleapiclient import discovery
from google.oauth2 import service_account
import hashlib

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
client_id = app.config["MY_STRAVA_CLIENT_ID"]
client_secret = app.config["MY_STRAVA_CLIENT_SECRET"]
url = app.config["MY_STRAVA_URL"]
google_private_key = app.config["GOOGLE_PRIVATE_KEY"]
google_private_key = google_private_key.replace('\\n', '\n')
spreadsheet_id = app.config["GOOGLE_SPREADSHEET_ID"]
range_name = app.config["GOOGLE_CELL_RANGE"]
google_client_email = app.config["GOOGLE_CLIENT_EMAIL"]
my_strava_club_id = app.config["MY_STRAVA_CLUB_ID"]


# define routes
@app.route("/")
def main():
    client = Client()
    auth_url = client.authorization_url(client_id=client_id,
                                        redirect_uri=url + 'authorization')
    return render_template('index.html', auth_url=auth_url)


@app.route("/authorization")
def authorization():
    code = request.args.get('code')
    client = Client()
    access_token = client.exchange_code_for_token(client_id=client_id,
                                                  client_secret=client_secret,
                                                  code=code)
    with open('access_token.json', 'w') as f:
        f.write(json.dumps(access_token))
    return render_template('authorization.html', access_token=access_token)


def get_google_credentials():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    account_info = {
        "private_key": google_private_key,
        "client_email": google_client_email,
        "token_uri": "https://accounts.google.com/o/oauth2/token",
    }

    credentials = service_account.Credentials.from_service_account_info(account_info, scopes=scopes)
    return credentials


def get_google_service(service_name='sheets', api_version='v4'):
    credentials = get_google_credentials()
    service = googleapiclient.discovery.build(service_name, api_version, credentials=credentials)
    return service


def write_to_google_sheet(values):
    service = get_google_service()
    body = {
        'values': values
    }
    value_input_option = 'RAW'
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()

@app.cli.command()
def pull():
    """Pulling activities"""
    access_token = get_strava_access_token()
    click.echo('Begin pulling activities')
    client = Client(access_token=access_token)
    data = []
    for athlete in client.get_club_activities(my_strava_club_id):
        data.append(to_array(athlete))
    click.echo('Update activities')
    write_to_google_sheet(data)
    click.echo('End pulling activities')


def get_strava_access_token():
    f = open('access_token.json', )
    data = json.load(f)
    access_token = data['access_token']
    f.close()
    return access_token


def to_array(activity_obj) -> list:
    obj = []
    obj.append(activity_obj.name)
    obj.append(str(activity_obj.start_date_local))
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


if __name__ == '__main__':
    app.run()
