
from django.conf.urls import include, url
from django.contrib import admin
import views


urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout/$', views.logout, name='logout'),

    url(r'^addRoom/$', views.addRoom, name='addRoom'),
    url(r'^delRoom/$', views.delRoom, name='delRoom'),
    url(r'^editRoom/$', views.editRoom, name='editRoom'),
    url(r'^sendEmailToInterviewer/$', views.sendEmailToInterviewer, name='sendEmail'),
    url(r'^roomManage/$', views.roomManage, name='roomManage'),
    url(r'^candidateManage/$', views.candidateManage, name='candidateManage'),
    url(r'^HRManage/$', views.showHRManage, name='HRManage'),
    #url(r'^showCandidate/$', views.showHRManage, name='showHRManage'),
    url(r'^addCandidate/$', views.addCandidate, name='addCandidate'),
    url(r'^delCandidate/$', views.delCandidate, name='delCandidate'),
    url(r'^editCandidate/$', views.editCandidate, name='editCandidate'),
    url(r'batchImportCandidate/$', views.batchImportCandidate, name='batchImportCandidate'),

    url(r'^sendEmailToCandidate/$', views.sendEmailToCandidate, name='sendEmailToCandidate'),
    url(r'^getInterviewerURL/$', views.getInterviewerURL, name='getInterviewerURL'),
    url(r'^getCandidateURL/$', views.getCandidateURL, name='getCandidateURL'),
    url(r'^downloadExampleExcel/$', views.downloadExampleExcel, name='downloadExampleExcel'),
]