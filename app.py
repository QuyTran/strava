from flask import Flask, request
from flask import render_template
import click
import googlemodel
import stravamodel

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# define routes
@app.route("/")
def main():
    client_id = app.config["MY_STRAVA_CLIENT_ID"]
    client_secret = app.config["MY_STRAVA_CLIENT_SECRET"]
    host = app.config["HOST_URL"]
    my_strava_club_id = app.config["MY_STRAVA_CLUB_ID"]
    strava_instance = stravamodel.StravaModel(my_strava_club_id, client_id, client_secret, host)
    auth_url = strava_instance.get_auth_url()
    return render_template('index.html', auth_url=auth_url)


@app.route("/authorization")
def authorization():
    code = request.args.get('code')
    strava_instance = stravamodel.StravaModel(app.config["MY_STRAVA_CLUB_ID"],
                                  app.config["MY_STRAVA_CLIENT_ID"],
                                  app.config["MY_STRAVA_CLIENT_SECRET"],
                                  app.config["HOST_URL"]
                                  )
    access_token = strava_instance.save_access_token(code)
    return render_template('authorization.html', access_token=access_token)


@app.cli.command()
def pull():
    """Pulling activities"""
    click.echo('Update activities')
    try:
        strava_instance = stravamodel.StravaModel(app.config["MY_STRAVA_CLUB_ID"],
                                      app.config["MY_STRAVA_CLIENT_ID"],
                                      app.config["MY_STRAVA_CLIENT_SECRET"],
                                      app.config["HOST_URL"]
                                      )
        data = strava_instance.get_club_activities(app.config["START_EVENT_ID"])
        google_instance = googlemodel.GoogleModel(app.config["GOOGLE_PRIVATE_KEY"],
                                      app.config["GOOGLE_SPREADSHEET_ID"],
                                      app.config["GOOGLE_CELL_RANGE"],
                                      app.config["GOOGLE_CLIENT_EMAIL"]
                                      )
        google_instance.write_to_google_sheet(data)
    except Exception as e:
        app.logger.info("Oops!", e.__class__, "occurred.")
    click.echo('End pulling activities')


if __name__ == '__main__':
    app.run()
