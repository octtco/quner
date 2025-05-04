from django.shortcuts import render, redirect
from django.utils.deprecation import MiddlewareMixin

class UserMiddleware(MiddlewareMixin):
    # 路由前处理
    def process_request(self, request):
        path = request.path_info
        if path == '/app/login/' or path == '/app/register/':
            return None
        else:
            username = request.session.get('username')
            if username:
                return None
            else:
                return redirect('/app/login/')
    # view前处理
    def process_view(self,request,callback,callback_args,callback_kwargs):
        pass
    # view后处理
    def process_response(self,request,response):
        return response