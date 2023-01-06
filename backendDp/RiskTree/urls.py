from django.urls import path
from . import views

# path('RiskTree/', include('RiskTree.urls')),
urlpatterns = [
    path('FileReceive/', views.fileReceive),
    path('RiskTreeData/', views.riskTree),
    path('QueryWheres/', views.QueryWheres),
    path('BSTTreeData/', views.BSTTree),

    path('DataDistribution/', views.DataDistribution),
]
