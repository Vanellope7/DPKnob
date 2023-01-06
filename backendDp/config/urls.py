from django.contrib import admin
from django.urls import path, include

from BaseDp.views import listorders
from DpDecisionMaker.views import getEpsilon

urlpatterns = [
    path('admin/', admin.site.urls),

    path('BaseDp/', listorders),

    path('AttackSimulation/', include('AttackSimulation.urls')),
    path('DpDecisionMaker/', include('DpDecisionMaker.urls')),
    path('RiskTree/', include('RiskTree.urls')),
]