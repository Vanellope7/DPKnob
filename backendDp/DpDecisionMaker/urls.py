from django.urls import path
from . import views

# path('DpDecisionMaker/', include('DpDecisionMaker.urls')),
urlpatterns = [
    # path('GetEpsilon/', getEpsilon),
    path('UpdateEpsilonWithPrivacy/', views.UpdateEpsilonWithPrivacy),
    path('UpdateEpsilonWithAccuracy/', views.UpdateEpsilonWithAccuracy)
]
