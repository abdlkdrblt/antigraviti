from django.urls import path
from . import views

urlpatterns = [
    path('plan/<int:pk>/', views.diet_plan_detail_view, name='diet_plan_detail'),
    path('plan/<int:pk>/pdf/', views.export_pdf_view, name='export_pdf'),
    
    # API Endpoints
    path('api/patient-calories/<int:pk>/', views.get_patient_calories, name='api_patient_calories'),
    path('api/food-data/', views.get_food_data, name='api_food_data'),
    path('api/food-groups/', views.get_food_group_data, name='api_food_groups'),
    path('api/exchanges/', views.get_exchanges, name='api_exchanges'),
    path('api/get-exchange-list/<int:content_type_id>/<int:object_id>/', views.get_exchange_list, name='get_exchange_list'),
]
