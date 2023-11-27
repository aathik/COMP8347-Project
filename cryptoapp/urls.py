from django.conf.urls.static import static
from django.urls import path
from . import views
from django.conf import settings

app_name = 'cryptoapp'

urlpatterns = [
    # Define a URL pattern for the user dashboard view
    # path('')
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_view'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('edit_info/', views.edit_profile, name='edit_info'),

    path('make_payment/<str:currency_to>/<int:order_amount>', views.make_payment, name='make_payment'),
    path('payment_success/<int:transaction_id>', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failure, name='payment_failure'),
    path('logout/', views.logout_view, name='user_logout'),

    path(r'payment_history/', views.payment_history, name='payment_history'),
    path(r'update_balance/<int:transaction_id>/', views.update_balance, name='update_balance'),
    path(r'delete_object/<int:pk>/', views.delete_object, name='delete_object'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('user_photos/', views.user_dashboard, name='photo',),
    path('logout/', views.logout_view, name='logout_view'),

    path(r'homepage/', views.homepage, name='homepage'),
    path(r'bitcoin-chart/', views.bitcoin_chart, name='bitcoin_chart'),

    # path('market/', views.market, name='market'),
    path('currency/<str:name>/', views.currency_detail, name='currency_detail'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
