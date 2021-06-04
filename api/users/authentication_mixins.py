from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import get_authorization_header

from api.users.authentication import ExpiringTokenAuthentication

class Authentication(object):
    user = None
    user_token_expired = False
    
    def get_user(self,request):
        """
        Return:
            * user      : User Instance or 
            * message   : Error Message or 
            * None      : Corrup Token
        """
        #print ("Authentication get_user 1")
        token = get_authorization_header(request).split()
        #print (f"Authentication get_user 2 request {request}")
        if token:
            try:
                token = token[1].decode()
                #print ("Authentication get_user 3")
            except:
                #print ("Authentication get_user 4")
                return None            
        
            #print ("Authentication get_user 5")
            token_expire = ExpiringTokenAuthentication()
            #print ("Authentication get_user 6")
            user,token,message,self.user_token_expired = token_expire.authenticate_credentials(token)
            #print ("Authentication get_user 7")
            
            if user != None and token != None:
                #print ("Authentication get_user 8")
                self.user = user
                return user
            
            #print ("Authentication get_user 9")
            return message
        
        #print ("Authentication get_user 10")
        return None

    def dispatch(self, request, *args, **kwargs):
        user = self.get_user(request)
        #print(f"user {request.user}")

        # found token in request
        if user is not None:
            """
            Possible value of variable user:
            * User Instance
            * Message like: Token Inválido, Usuario no activo o eliminado, Su Token ha expirado
            """
            if type(user) == str:
                response = Response({'error':user
                                  ,'expired':self.user_token_expired}
                                    ,status = status.HTTP_400_BAD_REQUEST)
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = 'application/json'
                response.renderer_context = {}
                return response
            
            # only user_token_expired = True, the request can be continue
            if not self.user_token_expired:
                return super().dispatch(request, *args, **kwargs)
        
        response = Response({'error': 'No se han enviado las credenciales.'
                          ,'expired': self.user_token_expired}
                            ,status = status.HTTP_400_BAD_REQUEST)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        return response
