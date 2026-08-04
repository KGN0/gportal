from django.shortcuts import redirect

class LogoutOnRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We bypass the admin panel and our internal API routes 
        # so we don't accidentally log out users during form submissions
        if not request.path.startswith('/api/') and not request.path.startswith('/admin/'):
            
            # 1. Check if the user is logged in (Our portal checks for 'mobile' in session)
            if 'mobile' in request.session:
                
                # 2. Check if a session flag exists. If it does, this is a page refresh/new request.
                if request.session.get('is_loaded', False):
                    
                    # Flush the session to log them out securely
                    request.session.flush()
                    # Cleanup the session flag (flush already removes it, but following your logic)
                    request.session['is_loaded'] = False 
                    
                    # Redirect to homepage
                    return redirect('/') 
                
                # 3. If it is their first time viewing the page after login, set the flag.
                request.session['is_loaded'] = True

        response = self.get_response(request)
        return response