"""
URL configuration for VotingProj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from votoAppWSServer.views import CensoView, VotoView, ProcesoElectoralView
from votoAppWSServer import views

urlpatterns = [
    path("censo/", CensoView.as_view(), name="censo"),
    path("voto/", VotoView.as_view(), name="voto"),
    path("procesoelectoral/<str:idProcesoElectoral>/", ProcesoElectoralView.as_view(), name="procesoelectoral"),
    path("voto/<str:id_voto>/", VotoView.as_view(), name="voto"),
    path('voto/<str:id_voto>/', VotoView.as_view(), name='delvoto'),
    path('testbd/', views.testbd, name='testbd'),
]
