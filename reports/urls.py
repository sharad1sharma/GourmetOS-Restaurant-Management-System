from django.urls import path
from .views import DailySalesReportView, StockAlertsReportView

urlpatterns = [
    path('reports/daily-sales/', DailySalesReportView.as_view(), name='daily-sales-report'),
    path('reports/stock-alerts/', StockAlertsReportView.as_view(), name='stock-alerts-report'),
]
