from datetime import datetime
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import(
    authenticate,
    get_user_model,
    login,
    logout
    )

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from api.users.serializers import *

#from api.users.views import CustomLoginSchema

class UserToken(APIView): 
    """
    Return Token for an username sended
    """

    def get(self,request,*args,**kwargs):
        username = request.GET.get('username')

        if not reglaActiva (username):
            return Response({'error':'Usuario presenta un problema. Comuníquese con el administrador'}, 
                        status = status.HTTP_401_UNAUTHORIZED)

        try:
            user_token = Token.objects.get(
                user = UserTokenSerializer().Meta.model.objects.filter(username = username).first()
            )
            return Response({
                'token': user_token.key
            })
        except:
            return Response({
                'error': 'Sesión a sido cerrada. Ingrese de nuevo'
            },status = status.HTTP_400_BAD_REQUEST)


class Login(ObtainAuthToken, CustomLoginSchema):

    def post(self,request,*args,**kwargs):
        """
        print(request.data)
        username = request.POST.get('username')
        password = request.POST.get('password')
        print (f"username {username} password {username}")
        """
        # send to serializer username and password
        login_serializer = self.serializer_class(data = request.data, context = {'request':request})
        if login_serializer.is_valid():
            # login serializer return user in validated_data

            user = login_serializer.validated_data['user']
            if user.is_active:
                if not reglaActiva (user.username):
                    return Response({'error':'Este usuario no puede iniciar sesión'}, 
                                status = status.HTTP_401_UNAUTHORIZED)


                token,created = Token.objects.get_or_create(user = user)
                user_serializer = UserTokenSerializer(user)
                if created:
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    }, status = status.HTTP_201_CREATED)
                else:
                    """
                    all_sessions = Session.objects.filter(expire_date__gte = timezone.now())
                    all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                    if all_sessions.exists():
                        for session in all_sessions:
                            session_data = session.get_decoded()
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                    
                    token = Token.objects.create(user = user)
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    }, status = status.HTTP_201_CREATED)
                    """
                    #token.delete()
                    return Response({
                        'error': 'Ya se ha iniciado sesión con este usuario. %s' %user.username
                    }, status = status.HTTP_409_CONFLICT)
            else:
                return Response({'error':'Este usuario no puede iniciar sesión - (u).'}, 
                                    status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Nombre de usuario o contraseña incorrectos.'},
                                    status = status.HTTP_400_BAD_REQUEST)
def reglaActiva (username):
    try:
        reglas = ApiReglasClientes.objects.get(username = username, estado_regla = 'Activo')
        #print (f"Login cliente_estado_facturacion *{reglas.cliente.cliente_estado_facturacion}*") 
        #Valida si el cliente es activo
        if not (reglas.cliente.cliente_estado_facturacion == "S" 
            or reglas.cliente.cliente_estado_facturacion == "C"):
            return False
    except ApiReglasClientes.DoesNotExist:
        return False
    return True

class Logout(APIView):

    def get(self,request,*args,**kwargs):
        try:
            elToken = request.GET.get('token')

            """
            print (f"token {token}" )
            for elT in Token.objects.all():
                print (f"user {elT.user} token {elT.key}")
            """

            token = Token.objects.get(key = elToken)

            #print (f"login token key {token.key} user {token.user}")

            if token:
                user = token.user

                #print(f"1 user {user} id {user.id}");

                all_sessions = Session.objects.filter(expire_date__gte = timezone.now())
                
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        # search auth_user_id, this field is primary_key's user on the session

                        uid = session_data.get('_auth_user_id')
                        if uid:
                            """
                            print (f"uid {uid } type {type(uid)}")
                            user = User.objects.get(pk=uid)
                            print (f"username {user.username }" )

                            """
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                # delete user token
                token.delete()
                
                session_message = 'Sesiones de usuario eliminadas.'  
                token_message = 'Token eliminado.'
                return Response({'token_message': token_message,'session_message':session_message},
                                    status = status.HTTP_200_OK)
            username = request.GET.get('username')    
            logout(request)
            return Response({'error':'No se ha encontrado un usuario con estas credenciales.'
                , 'username':username},
                status = status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            username = request.GET.get('username')    
            logout(request)
            return Response({'error': 'No se ha encontrado token en la petición.'
                , 'username':username},
                status = status.HTTP_409_CONFLICT)
        

