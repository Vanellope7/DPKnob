from django.urls import path
from . import views

# path('AttackSimulation/', include('AttackSimulation.urls')),
urlpatterns = [
    path('GetNoisyDataDistribution/', views.GetNoisyDataDistribution),
    path('GetPrivacyDistribution/', views.GetPrivacyDistribution),
    path('GetOppositeProbability/', views.GetOppositeProbability),
    path('GetGeneralQueryDistribution/', views.GetGeneralQueryDistribution),

]
