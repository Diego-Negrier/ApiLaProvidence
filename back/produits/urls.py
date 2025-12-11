from django.urls import path
from .views import ProduitListView, ProduitDetailView

app_name = "produits"

urlpatterns = [
    path('', ProduitListView.as_view(), name='liste'),
    path('<slug:slug>/', ProduitDetailView.as_view(), name='detail'),
]
