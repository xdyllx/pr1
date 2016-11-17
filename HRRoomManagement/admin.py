#coding=utf-8
__author__ = 'Xu Dongyi'

from HRRoomManagement.models import Interviewer, Interview, Candidate
from django.contrib import admin


admin.site.register(Interviewer)
admin.site.register(Interview)
admin.site.register(Candidate)

