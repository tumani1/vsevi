# coding: utf-8

from django.conf.urls import patterns, url
from apps.users import views

urlpatterns = patterns('',
    url(r'^forgotpwd/$', views.ResetPasswordView.as_view(), name='restore_password'),
    url(r'^confirm-email/$', views.ConfirmEmailView.as_view(), name='confirm_email'),
    url(r'^profile/$', views.UserProfileView.as_view(), name='profile_view'),
    url(r'^users/(?P<user_id>\d+)/$', views.UserView.as_view()),
    url(r'^stream/$', 'apps.users.views.feed_view', name='user_feed_view'),
    url(r'^register/$', views.RegisterUserView.as_view()),
    url(r'^logout/(?P<provider>[a-zA-Z0-9-]+)/$', views.delete_social_provider),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'apps.users.views.password_reset_confirm', name="password_reset"),

    # Auth
    url(r'^login/$', views.LoginUserView.as_view(), name='login_view'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='logout_view'),
    url('^tokenize/?$', views.TokenizeView.as_view(), name="tokenize"),
)

