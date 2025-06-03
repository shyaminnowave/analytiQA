from abc import ABCMeta



class APIClient:

    def __init__(self, endpoint, headers):
        self.base_url = endpoint
        self.headers = headers


    def make_request(self, method, endpoint, params=None, data=None, headers=None):
        pass

    @property
    def get_headers(self):
        return self.headers
    