from django.conf.urls import url
from Bookmis import views

urlpatterns = [
    url(r'^$', views.index, name='homepage'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^set_password/$', views.set_password, name='set_password'),
    url(r'^add_book/$', views.add_book, name='add_book'),
    url(r'^view_book_list/$', views.view_book, name='view_book'),
    url(r'^view_book_list/detail/$', views.detail, name='detail'),
    url(r'^borrow/$', views.borrow, name='borrow'),
    url(r'^borrow_info/$', views.borrow_info, name='borrow_info'),
    url(r'^return_book/$', views.return_book, name='return_book'),
    url(r'^book_lost/$', views.book_lost, name='book_lost'),
    url(r'^level_up/$', views.level_up, name='level_up'),
    url(r'^level_up/level_success/$', views.level_success, name='level_success'),
    url(r'^loss_report/$', views.loss_report, name='loss_report'),
    url(r'^late_return',views.late_return, name='late_return'),
]