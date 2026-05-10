import re
import os
import json
import requests
import sys
from future.utils import raise_from


class Auth:

    def __init__(self, url, sslcert=None, **kwargs):
        self._url = url
        self._sslcert = sslcert
        if sslcert is not None and not os.path.isfile(sslcert):
            raise FileNotFoundError(
                'sslcert file "{}" not found'.format(sslcert))
        if {'email', 'password'} == set(kwargs):
            self._init_from_credentials(**kwargs)
        elif {'apikey'} == set(kwargs):
            self._init_from_apikey(**kwargs)
        elif {'clientkey'} == set(kwargs):
            self._init_from_clientkey(**kwargs)
        elif {'apikey', 'child_email'} == set(kwargs):
            self._init_from_child_email(**kwargs)
        elif {'apikey', 'child_ref'} == set(kwargs):
            self._init_from_child_ref(**kwargs)
        elif {'apikey', 'child_id'} == set(kwargs):
            self._init_from_child_id(**kwargs)
        else:
            raise KeyError('incorrect constructor args combination')

    def _init_from_credentials(self, email, password):
        self._auth = (email, password)
        self._headers = {'X-Auth-With-Account-Credentials': 'API'}

    def _init_from_apikey(self, apikey):
        self._auth = (apikey, '')
        self._headers = {}

    def _init_from_clientkey(self, clientkey):
        self._auth = (clientkey, '')
        self._headers = {'X-Auth-With-Client-Key': 'API'}

    def _init_from_child_email(self, apikey, child_email):
        self._auth = (apikey, '')
        self._headers = {'X-Child-Account-By-Email': child_email}

    def _init_from_child_ref(self, apikey, child_ref):
        self._auth = (apikey, '')
        self._headers = {'X-Child-Account-By-CreatorRef': child_ref}

    def _init_from_child_id(self, apikey, child_id):
        self._auth = (apikey, '')
        self._headers = {'X-Child-Account-By-Id': child_id}

    def get(self, endpoint, request_headers=None):
        return self._request(requests.get, endpoint, None, request_headers)

    def post(self, endpoint, fields=None, request_headers=None):
        return self._request(requests.post, endpoint, fields, request_headers)

    def patch(self, endpoint, fields=None, request_headers=None):
        return self._request(requests.patch, endpoint, fields, request_headers)

    def delete(self, endpoint, request_headers=None):
        return self._request(requests.delete, endpoint, None, request_headers)

    def _request(self, method, endpoint, fields=None, request_headers=None):
        # request handling

        # :param method      - requests.(get/post/patch/delete)
        # :param endpoint    - https://api.printnode.com/(endpoint)
        # :param fields      - data fields to be sent with a post or patch
        # :param request_headers- if a function requires an extra header or has
        # custom user set headers, add them to _headers

        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        other_args = {}
        if fields is not None:
            other_args['data'] = json.dumps(fields)
        if request_headers is None:
            request_headers = self._headers
        else:
            request_headers.update(self._headers)

        if method == requests.patch:
            request_headers.update({"Content-Type": "application/json"})

        if self._sslcert is not None:
            other_args['verify'] = self._sslcert
        url = self._url + endpoint
        with rewrite_requests_error():
            response = method(
                url=url,
                auth=self._auth,
                headers=request_headers,
                **other_args)

        content_type = response.headers.get('content-type')
        if content_type != 'application/json':
            template = 'Incorrect Content-Type "{}" for url "{}"'
            raise ValueError(template.format(content_type, url))
        response_obj = response.json()
        if sys.version_info[0] < 3:
            response_obj = self._fix_unicode(response_obj)

        if 401 == response.status_code:
            raise Unauthorized(response.status_code, **response_obj)
        elif 429 == response.status_code:
            raise TooManyRequests(response.status_code, **response_obj)
        elif self._is_hundreth(4, response.status_code):
            raise ClientError(response.status_code, **response_obj)
        elif self._is_hundreth(5, response.status_code):
            raise ServerError(response.status_code, **response_obj)
        elif self._is_hundreth(2, response.status_code):
            return response_obj
        else:
            raise Exception('status code: ' + str(response.status_code))

    def _is_hundreth(self, hundreth, number):
        pattern = str(hundreth) + r'\d{2,}'
        return bool(re.match(pattern, str(number)))

    def _fix_unicode(self, json_object):
        returnvalue = json_object
        if type(json_object) is dict:
            returnvalue = {}
            for k, v in json_object.iteritems():
                if type(k) is unicode:
                    k = k.encode('utf-8')
                if type(v) is dict or type(v) is list:
                    v = self._fix_unicode(v)
                if type(v) is unicode:
                    v = v.encode('utf-8')
                returnvalue.update({k: v})
        if type(json_object) is list:
            returnvalue = []
            for x in json_object:
                if type(x) is unicode:
                    x = x.encode('utf-8')
                if type(x) is dict or type(x) is list:
                    x = self._fix_unicode(x)
                returnvalue.append(x)
        if type(json_object) is unicode:
            returnvalue = json_object.encode('utf-8')
        return returnvalue


class ApiError(RuntimeError):
    def __init__(self, status_code, code, message, uid=None, **remaining):
        super(ApiError, self).__init__('{}({}): {}'.format(
            code,
            status_code,
            message))
        self.status_code = status_code
        self.code = code
        self.message = message
        self.uid = uid


class ClientError(ApiError):
    pass


class Unauthorized(ClientError):
    pass


class TooManyRequests(ClientError):
    pass


class ServerError(ApiError):
    pass


class NetworkError(RuntimeError):
    pass


class TimeoutError(NetworkError):
    pass


class TooManyRedirectsError(NetworkError):
    pass


class ConnectionError(NetworkError):
    pass


class HttpError(NetworkError):
    pass


class RequestError(NetworkError):
    pass


class rewrite_requests_error:

    mapping = {
        requests.Timeout: TimeoutError,
        requests.TooManyRedirects: TooManyRedirectsError,
        requests.HTTPError: HttpError,
        requests.ConnectionError: ConnectionError}

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            return
        exc = self.mapping.get(exc_type, RequestError)
        raise_from(exc(str(exc_value)), exc_value)
