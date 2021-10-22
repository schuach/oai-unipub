import os

# get data von environ
# setup for venv: https://stackoverflow.com/questions/9554087/setting-an-environment-variable-in-virtualenv
class Config(object):
    FTP_URL = os.environ.get("FTP_URL") or "localhost"
    FTP_USER = os.environ.get("FTP_USER") or "oaitest"
    FTP_PASS = os.environ.get("FTP_PASS") or "oaitest"
    DATA_DIR = os.environ.get("DATA_DIR") or "data"
