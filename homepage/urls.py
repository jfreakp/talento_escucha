from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.home, name='home'),
    path('servicios/', views.servicios, name='servicios'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('solicitud-usuario/', views.solicitud_usuario, name='solicitud_usuario'),
    path('solicitud-anonimo/', views.solicitud_anonimo, name='solicitud_anonimo'),
    path('buscar-ticket/', views.buscar_ticket, name='buscar_ticket'),
    path('test-styles/', views.test_styles, name='test_styles'),
]