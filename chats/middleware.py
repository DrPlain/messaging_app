from datetime import datetime, timedelta
import logging
from datetime import datetime
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponseForbidden
from django.utils.timezone import localtime, now, timedelta
import pytz
# from django.contrib.gis.geoip2 import GeoIP2


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        user = self._authenticate_request(request)

        with open('requests.log', 'a') as f:
            f.write(
                f"{datetime.now()} - User: {user if user else 'AnonymousUser'} - Path: {request.path} - IP: {request.META['REMOTE_ADDR']}\n")
        response = self.get_response(request)
        return response

    def _authenticate_request(self, request):
        """Manually authenticate the request using JWT."""
        try:
            jwt_auth = JWTAuthentication()
            auth_header = get_authorization_header(request)
            if auth_header:
                user, _ = jwt_auth.authenticate(request)
                return user
        except Exception as e:
            self.logger.error(f"JWT Authentication failed: {e}")
        return None


class RestrictAccessByTimeMiddleware:
    """a middleware that restricts access to the messaging up during certain hours of the day outside 9PM and 6PM"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.start_time = 21
        self.end_time = 18

    def __call__(self, request):
        user_timezone = pytz.timezone("Africa/Lagos")
        utc_current_time = now()
        user_current_localtime = localtime(utc_current_time, user_timezone)
        # print(utc_current_time, user_current_localtime)
        if user_current_localtime.hour < 21 and user_current_localtime.hour > 18:
            return HttpResponseForbidden('Access restricted during this time')

        return self.get_response(request)

    # def _get_user_local_timezone(self, request):
    #     ip = request.META['REMOTE_ADDR']
    #     g = GeoIP2()
    #     user_location = g.city(ip)
    #     user_timezone = user_location['time_zone']
    #     return user_timezone


class RestrictNumberOfPostMessages:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_request_data = {}  # Dictionary to track request data by IP

    def __call__(self, request):
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            current_time = now()

            # Initialize or update data for the IP address
            if ip not in self.ip_request_data:
                self.ip_request_data[ip] = {
                    'start_time': current_time,
                    'request_count': 1
                }
            else:
                ip_data = self.ip_request_data[ip]
                elapsed_time = current_time - ip_data['start_time']

                if elapsed_time >= timedelta(minutes=1):
                    # Reset count and start time after the time window
                    ip_data['start_time'] = current_time
                    ip_data['request_count'] = 1
                else:
                    # Increment request count if within time window
                    ip_data['request_count'] += 1

                    # Check if request limit exceeded
                    if ip_data['request_count'] > 5:
                        return HttpResponseForbidden('You cannot send more than 5 messages in a minute!')

        # Pass the request to the next middleware or view
        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        """Extract the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        print(x_forwarded_for)
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
