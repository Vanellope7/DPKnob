from django.urls import path
from . import views

# path('DpDecisionMaker/', include('DpDecisionMaker.urls')),
urlpatterns = [
    # path('GetEpsilon/', getEpsilon),
    path('UpdateEpsilonWithPrivacy/', views.UpdateEpsilonWithPrivacy),
<<<<<<< HEAD
    path('UpdateEpsilonWithAccuracy/', views.UpdateEpsilonWithAccuracy)
=======
    path('UpdateEpsilonWithAccuracy/', views.UpdateEpsilonWithAccuracy),
    path('GetAccuracyDeviationP/', views.GetAccuracyDeviationP),
    path('GetPrivacyDeviationP/', views.GetPrivacyDeviationP)
>>>>>>> ec03867 (initial)
]
