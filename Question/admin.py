#coding=utf-8

from Question.models import Choice, Completion, Essay, Code
from django.contrib import admin


admin.site.register(Choice)
admin.site.register(Completion)
admin.site.register(Essay)
admin.site.register(Code)

