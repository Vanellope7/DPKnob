from django.contrib import admin
from django.urls import path, include

from BaseDp.views import listorders
<<<<<<< HEAD
from DpDecisionMaker.views import getEpsilon
=======
>>>>>>> ec03867 (initial)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('BaseDp/', listorders),

    path('AttackSimulation/', include('AttackSimulation.urls')),
    path('DpDecisionMaker/', include('DpDecisionMaker.urls')),
    path('RiskTree/', include('RiskTree.urls')),
]