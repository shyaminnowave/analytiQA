import logging
import json
import requests
from abc import ABC, abstractmethod, ABCMeta
from apps.stb.models import STBAuthToken
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException, Timeout, ConnectionError


class APIError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class BaseAPIClient(metaclass=ABCMeta):

    """
    Abstract base class for API clients.
    """

    @abstractmethod
    def make_request(self, method: str, endpoint: str, params: Optional[Dict]=None, data: Optional[Union[Dict, str]]=None,
                     headers: Optional[Dict]=None):
        pass

    @abstractmethod
    def get(self, endpoint: str, params: Optional[Dict]=None, headers: Optional[Dict]=None):
        pass

    @abstractmethod
    def post(self, endpoint: str, params: Optional[Dict]=None, data: Optional[Union[Dict, str]]=None,
                     headers: Optional[Dict]=None):
        pass


class APIClient(BaseAPIClient):

    def make_request(self, method: str, endpoint: str, params: Optional[Dict]=None, data: Optional[Union[Dict, str]]=None,
                     headers: Optional[Dict]=None):
        request_headers = headers
        logger = logging.getLogger(__name__)
        logger.debug(f"Making {method} request to {endpoint}")
        try:
            response = requests.request(method, endpoint, params=params, data=data, headers=request_headers)
            return response
        except ConnectionError as e:
            logger.error(str(e))
            return None

    def get(self, endpoint: str = None, params: Optional[Dict]=None, headers: Optional[Dict]=None):
        return self.make_request('GET', endpoint=endpoint, params=params, headers=headers)

    def post(self, endpoint: str = None, params: Optional[Dict]=None, data: Optional[Union[Dict, str]]=None,
                     headers: Optional[Dict]=None):
        return self.make_request('POST', endpoint=endpoint, params=params, data=data, headers=headers)


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
            return "https://innowave.stb-tester.com/api/v2/"
            # url = STBUrl.objects.get()
            # return url.endpoint
        except Exception as e:
            logging.error(f"Failed to retrieve STB URL: {str(e)}")
            raise

    @staticmethod
    def get_token(request=None) -> Optional[str]:
        """
        Get the access token from the database.

        Returns:
            String containing the access token for the STB API

        Raises:
            Exception: If the token cannot be retrieved
        """
        try:
            if request:
                token = STBAuthToken.objects.get(user=request.user)
            else:
                token = STBAuthToken.objects.get(user='shyam6132@gmail.com')
            return token.get_authorization_token
        except STBAuthToken.DoesNotExist:
            logging.warning("STB token not found")
            return None
        except Exception as e:
            logging.error(f"Failed to retrieve STB token: {str(e)}")
            raise APIError(f"Failed to retrieve STB token: {str(e)}") from e



class STBClient:

    def __init__(self, baseurl=None, request=None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.baseurl = baseurl or STBRepository.get_base_url()
        self.request = request
        self.client = APIClient()


    @staticmethod
    def generate_results_url(testscript, date=None):
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

    @staticmethod
    def get_headers(request) -> str:
        token = STBRepository.get_token(request)
        return token

    def get_results(self, testscript, date=None):
        get_token = self.get_headers(self.request)
        endpoint = f"{self.baseurl}{self.generate_results_url(testscript, date=date)}"
        try:
            self.logger.info(f"Fetching results for testcase {testscript}")
            response = self.client.get(endpoint, headers=get_token)

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


    def get_stb_node_info(self):
        get_token = self.get_headers(self.request)
        try:
            response = self.client.get(endpoint=self.baseurl, headers=get_token)
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Run test result: {result}")
                return result
            elif response.status_code in [400, 403, 500]:
                self.logger.warning(f"Access forbidden")
                return None
        except APIError as e:
            self.logger.error(f"API Error: {e.message}, Status: {e.status_code}")
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")

    def get_node_status(self):
        endpoint = f"{self.baseurl}/nodes"
        get_token = {
            "Authorization": "token 1TUvMNqfshWzQPhWNztb0eJOWfx7G_RV",
        }
        try:
            self.logger.info(f"Fetching node status")
            response = self.client.get(endpoint, headers=get_token)
            if response.status_code == 200:
                data = response.json()
                _status = []
                for i in range(len(data)):
                    temp = {
                        "node_id": data[i]["node_id"],
                        "status": data[i]["available"],
                    }
                    _status.append(temp)
                self.logger.info(f"Fetching node status")
                return _status
            elif response.status_code == 404:
                self.logger.warning(f"Access forbidden")
                return []
            else:
                self.logger.error(f"API returned unexpected status code: {response.status_code}")
                return None
        except APIError as e:
            self.logger.error(f"API Error: {e.message}, Status: {e.status_code}")
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")


    def get_testcase_names(self, branch):
        # get_token = self.get_headers(self.request)
        endpoint = f"{self.baseurl}test_pack/{branch}/test_case_names"
        get_token = {
            "Authorization": "token 1TUvMNqfshWzQPhWNztb0eJOWfx7G_RV",
        }

        try:
            self.logger.info(f"Fetching testcase names for branch: {branch}")
            response = self.client.get(endpoint, headers=get_token)
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
        get_token = {
            "Authorization": "token 1TUvMNqfshWzQPhWNztb0eJOWfx7G_RV",
        }
        endpoint = f"{self.baseurl}run_tests"
        _data = {
            "node_id": node_id,
            "test_cases": test_cases,
            "remote_control": remote_control,
            "test_pack_revision": test_pack_revision
        }
        if node_id and test_cases and remote_control and test_pack_revision:
            response = self.client.post(endpoint=endpoint, data=json.dumps(_data), headers=get_token)
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

    def __del__(self):
        self.logger.info(f"{self} - Deleting STB repository...")