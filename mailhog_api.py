
class MailhogApi:
    def __init__(self, host, headers=None):
        self.host = host
        self.headers = headers