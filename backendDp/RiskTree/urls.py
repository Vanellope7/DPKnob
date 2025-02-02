from django.urls import path
from . import views

# path('RiskTree/', include('RiskTree.urls')),
urlpatterns = [
    path('FileReceive/', views.fileReceive),
    path('RiskTreeData/', views.riskTree),
    path('QueryWheres/', views.QueryWheres),
    path('BSTTreeData/', views.BSTTree),
    path('DataDistribution/', views.DataDistribution), #平行坐标图
    path('getSensitivity/', views.getSensitivity),
    path('AvgRiskP/', views.AvgRiskP),
    path('initializeSchemeHistory/', views.initializeSchemeHistory),
    path('minSensitivityMap/', views.minSensitivityMap),
    path('curHighRiskSQL/', views.curHighRiskSQL)
]
