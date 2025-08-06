class NoCacheMiddleware:
    # Middleware to prevent caching of sensitive pages.
    # This ensures that after a user logs out, they cannot use the browser's back button
    # to access previously authenticated pages.
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Set Cache-Control headers to prevent caching by browsers and proxies.
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'  # For HTTP/1.0 compatibility
        response['Expires'] = '0'      # For HTTP/1.0 compatibility
        return response