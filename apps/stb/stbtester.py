import logging
import json
import requests
from dataclasses import dataclass
from apps.stb.models import STBUrl, STBToken
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
from requests.exceptions import RequestException, Timeout, ConnectionError


class APIError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


@dataclass
class APIClient:

    base_url: str
    headers: str

    @property
    def get_headers(self):
        return self.headers

    def make_request(self, method, endpoint=None, params=None, data=None, headers=None):
        if endpoint:
            url = urljoin(self.base_url, endpoint) 
        else:
            url = self.base_url
        request_headers = {**self.get_headers(), **(headers or {})}

        logger = logging.getLogger(__name__)
        logger.debug(f"Making {method} request to {url}")
        try:
            response = requests.request(method, url, params=params, data=data, headers=request_headers)
            return response
        except ConnectionError as e:
            logger.error(str(e))
            return None

    def get(self, endpoint=None, params=None, headers=None):
        return self.make_request('GET', endpoint, params, headers)

    def post(self, endpoint=None, params=None, data=None, headers=None):
        return self.make_request('POST', endpoint, params, data, headers)


class STBRepository:
    """
    Repository for accessing STB URL and token data from the database.
    This class encapsulates all database operations.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Get the base URL from the database.

        Returns:
            String containing the base URL for the STB API

        Raises:
            Exception: If the URL cannot be retrieved
        """
        try:
            url = STBUrl.objects.get()
            return url.endpoint
        except Exception as e:
            logging.error(f"Failed to retrieve STB URL: {str(e)}")
            raise

    @staticmethod
    def get_token() -> str:
        """
        Get the access token from the database.

        Returns:
            String containing the access token for the STB API

        Raises:
            Exception: If the token cannot be retrieved
        """
        try:
            token = STBToken.objects.get()
            return token
        except Exception as e:
            logging.error(f"Failed to retrieve STB token: {str(e)}")
            raise


class STBClient:

    def __init__(self, baseurl=None, headers=None):
        self.logger = logging.getLogger(__name__)
        self.baseurl = baseurl
        self.headers = headers
        # self.client = 

    def build_results_url(self, testscript, date=None):
        """
        This will build a URL based on the given testscript and date
        :param testscript:
        :param date:
        :return:
        """
        if date:
            return f'results?filter=testcase:{testscript}+date:>"{date}"&sort=date:asc'
        else:
            return f'results?filter=testcase:{testscript}&sort=date:asc'

    def get_results(self, testscript, date=None):
        endpoint = self.build_results_url(testscript, date=date)
        try:
            self.logger.info(f"Fetching results for testcase {testscript}")
            response = self.client.get(endpoint)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                self.logger.warning(f"Access forbidden for endpoint: {endpoint}")
                return []
            else:
                error_msg = f"API returned unexpected status code: {response.status_code}"
                self.logger.error(error_msg)
                try:
                    error_details = response.json()
                    raise APIError(error_msg, response.status_code, error_details)
                except ValueError:
                    raise APIError(error_msg, response.status_code)

        except APIError as e:
            self.logger.error(f"API Error: {e.message}, Status: {e.status_code}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")
        
    
    def get_stb_mode_info(self):
        try:
            self.logger.info(f"Fetching STB node info details")
            response = self.client.get()
        except Exception as e:
            pass


    def get_testcase_names(self, branch):
        endpoint = f"test_pack/{branch}/test_case_names"
        try:
            self.logger.info(f"Fetching testcase names for branch: {branch}")
            response = self.client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                test_cases = data if isinstance(data, list) else data.get("test_cases", [])
                self.logger.info(f"Fetched testcase names for branch: {branch}")
                return test_cases
            elif response.status_code == 404:
                self.logger.warning(f"Access forbidden for branch: {branch}")
                return []
            else:
                self.logger.error(f"API returned unexpected status code: {response.status_code}")
                return None
        except APIError as e:
            self.logger.error(f"API Error: {e.message}, Status: {e.status_code}")
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
        

    def run_testcase_by_name(self,
                             node_id: str,
                             test_cases: List[str],
                             remote_control: str,
                             test_pack_revision: str
                             ):
        endpoint = "run_tests"
        _data = {
            "node_id": node_id,
            "test_cases": test_cases,
            "remote_control": remote_control,
            "test_pack_revision": test_pack_revision
        }
        if node_id and test_cases and remote_control and test_pack_revision:
            response = self.client.post(endpoint, data=json.dumps(_data))
            print(response)
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                self.logger.info(f"Run test result: {result}")
                return result
            elif response.status_code == 403 or response.status_code == 404:
                self.logger.warning(f"Access forbidden for node_id: {node_id}")
                return None
            return None
        else:
            self.logger.error(f"Failed to run testcase: {test_cases}")
            return None