class Config(object):
    DEBUG = False
    TESTING = False
    HOST_URL = ""
    MY_STRAVA_CLIENT_ID = ""
    MY_STRAVA_CLIENT_SECRET = ""
    MY_STRAVA_CLUB_ID = ""
    GOOGLE_PRIVATE_KEY = ""
    GOOGLE_CLIENT_EMAIL = ""
    GOOGLE_SPREADSHEET_ID = ""
    GOOGLE_CELL_RANGE = ""
    START_EVENT_ID = ''
    SENTRY_DSN = ""


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
