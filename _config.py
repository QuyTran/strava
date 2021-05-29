class Config(object):
    DEBUG = False
    TESTING = False
    MY_STRAVA_CLIENT_ID =
    MY_STRAVA_CLIENT_SECRET = ""
    MY_STRAVA_URL = ""
    MY_STRAVA_CLUB_ID =
    GOOGLE_PRIVATE_KEY = ""
    GOOGLE_CLIENT_EMAIL = ""
    GOOGLE_SPREADSHEET_ID = ''
    # GOOGLE_SPREADSHEET_ID = ''
    GOOGLE_CELL_RANGE = ''


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
