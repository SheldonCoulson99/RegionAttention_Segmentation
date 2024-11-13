from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('start-segmentation/', views.start_segmentation, name='start_segmentation'),
    path('check-python/', views.check_python_version, name='check_python_version'),
    path('save_to_db/', views.save_to_db, name='save_to_db'),
    path('segmented-image/<uuid:image_id>/', views.get_segmented_image, name='get_segmented_image'),
    path('get-image/<str:image_type>/<uuid:image_id>/', views.get_image, name='get_image'),
    path('clear_monuseg/', views.clear_monuseg_visualize_test, name='clear_monuseg_visualize_test'),
    path('clear_isic/', views.clear_isic_visualize_test, name='clear_isic_visualize_test'),
]
