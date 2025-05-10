from django.http import HttpResponseForbidden

class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of blocked IP addresses
        blocked_ips = ['127.0.0.1', '192.168.0.1']  # Add the IPs you want to block

        # Get the user's IP address
        user_ip = request.META.get('REMOTE_ADDR')

        # Check if the user's IP is in the blocked list
        if user_ip in blocked_ips:
            return HttpResponseForbidden("Access Forbidden")

        return self.get_response(request)