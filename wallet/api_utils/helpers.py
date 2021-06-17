# helper functions
import requests
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def getUserIpAddress(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
    elif request.META.get('HTTP_X_FORWARDED_HOST'):
        ip = request.META.get('HTTP_X_FORWARDED_HOST')
    elif request.META.get('HTTP_X_FORWARDED_SERVER'):
        ip = request.META.get('HTTP_X_FORWARDED_SERVER')
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip


def getUserLocationData(ipAddress=None, httpRequest=None):
    try:
        if not ipAddress:
            ipAddress = getUserIpAddress(httpRequest)

        ipGeoLocationEndpoint = f"http://ip-api.com/json/{ipAddress}"
        payload = {"fields": "status,country,city,region,regionName,zip,timezone"}
        request = requests.get(ipGeoLocationEndpoint, params=payload)
        response = request.json()
        if request.status_code != 200:
            return response['message']
        
        city = response['city']
        # region = response['regionName']
        country = response['country']
        return f"{city}, {country}"
    
    except Exception as e:
        logger.error('getUserLocationData')
        logger.error(e)
        return None


class MultipleProxyMiddleware:
    FORWARDED_FOR_FIELDS = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED_HOST',
        'HTTP_X_FORWARDED_SERVER',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Rewrites the proxy headers so that only the client IP address is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if ',' in request.META[field]:
                    parts = request.META[field].split(',')
                    request.META[field] = parts[0].strip()
        return self.get_response(request)
