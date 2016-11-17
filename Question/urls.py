
from django.conf.urls import include, url
from django.contrib import admin
import views


urlpatterns = [
    url(r'^interviewerManage/$', views.showQuestions, name='showQuestions'),

    url(r'^checkVideoFilepath/$', views.checkVideoFilepath, name='checkVideoFilepath'),
    url(r'^downloadVideo/$', views.downloadVideo, name='downloadVideo'),
    url(r'^checkReportFilepath/$', views.checkReportFilepath, name='checkReportFilepath'),
    url(r'^downloadReport/$', views.downloadReport, name='downloadReport'),
    url(r'^checkFinalcodeFilepath/$', views.checkFinalcodeFilepath, name='checkFinalcodeFilepath'),
    url(r'^downloadFinalcode/$', views.downloadFinalcode, name='downloadFinalcode'),
    url(r'^checkWhiteboardFilepath/$', views.checkWhiteboardFilepath, name='checkWhiteboardFilepath'),
    url(r'^downloadWhiteboard/$', views.downloadWhiteboard, name='downloadWhiteboard'),
    url(r'^checkChatFilepath/$', views.checkChatFilepath, name='checkChatFilepath'),
    url(r'^downloadChat/$', views.downloadChat, name='downloadChat'),

    url(r'^getStatusAfterInterview/$', views.getStatusAfterInterview, name='getStatusAfterInterview'),  # API
    url(r'^getFilepathAfterInterview/$', views.getFilepathAfterInterview, name='getFilepathAfterInterview'),  # API
    
    url(r'^fileUpload/$', views.fileUpload, name='fileUpload'),

    url(r'^problems/$', views.getQuestionJsend, name='getQuestionJsend'),        # API
    url(r'^getCandidate/$', views.getCandidateJsend, name='getCandidateJsend'),  # API
    url(r'^getRoomId/$', views.getRoomJsend, name='getRoomJsend'),               # API

    url(r'^choiceManage/$', views.showChoice, name='showChoice'),
    url(r'^completionManage/$', views.showCompletion, name='showCompletion'),
    url(r'^essayManage/$', views.showEssay, name='showEssay'),
    url(r'^codeManage/$', views.showCode, name='showCode'),
    url(r'^intervieweeManage/$', views.showInterviewee, name='showInterviewee'),


    url(r'^addChoice/$', views.addChoice, name='addChoice'),
    url(r'^addCompletion/$', views.addCompletion, name='addCompletion'),
    url(r'^addEssay/$', views.addEssay, name='addEssay'),
    url(r'^addCode/$', views.addCode, name='addCode'),

    url(r'^delChoice/$', views.delChoice, name='delChoice'),
    url(r'^delCompletion/$', views.delCompletion, name='delCompletion'),
    url(r'^delEssay/$', views.delEssay, name='delEssay'),
    url(r'^delCode/$', views.delCode, name='delCode'),

    url(r'^editChoice/$', views.editChoice, name='editChoice'),
    url(r'^editCompletion/$', views.editCompletion, name='editCompletion'),
    url(r'^editEssay/$', views.editEssay, name='editEssay'),
    url(r'^editCode/$', views.editCode, name='editCode'),

    url(r'^getChoiceById/$', views.getChoiceById, name='getChoiceById'),
    url(r'^getCompletionById/$', views.getCompletionById, name='getCompletionById'),
    url(r'^getEssayById/$', views.getEssayById, name='getEssayById'),
    url(r'^getCodeById/$', views.getCodeById, name='getCodeById'),

]