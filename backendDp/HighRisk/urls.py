from django.urls import path
from . import views

# path('DpDecisionMaker/', include('DpDecisionMaker.urls')),
urlpatterns = [
    path('getKeyMap/', views.getKeyMap),
    path('HighRiskData/', views.highRiskData),
]
