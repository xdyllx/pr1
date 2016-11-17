#coding=utf-8

from django.db import models
from django.contrib.auth.models import User,auth

# CONST VALUE
NAME_MAX_LENGTH = 30
EMAIL_MAX_LENGTH = 50
PHONENUMBER_MAX_LENGTH = 20
STARTTIME_MAX_LENGTH = 40
LOGO_URL = 'logo'
LOGO_DEFAULT = 'blank.jpg'
EXCEL_URL = 'excel'
NUMBER_IN_PAGE = 10
CANDIDATE_PARAM_NUM = 4
# CANDIDATE STATE
NOT_START = 0
PASS_INTERVIEW = 1
NOT_PASS_INTERVIEW = 2
FILEPATH_MAX_LENGTH = 200



# 面试model
class Interview(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    startTime = models.CharField(max_length=STARTTIME_MAX_LENGTH)
    logo = models.ImageField(upload_to=LOGO_URL, default=LOGO_DEFAULT)
    def __str__(self):
        return self.name


# 面试官model
class Interviewer(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH)
    interview = models.ForeignKey(Interview)    # 面试官model里内含一个面试model
    def __str__(self):
        return self.name + ' ' + self.email

# 候选人model
class Candidate(models.Model):
    # personal info
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH)
    phoneNumber = models.CharField(max_length=PHONENUMBER_MAX_LENGTH)

    # interview
    interview = models.ForeignKey(Interview)
    state = models.SmallIntegerField(default=NOT_START)
    videopath = models.CharField(max_length=FILEPATH_MAX_LENGTH)
    reportpath = models.CharField(max_length=FILEPATH_MAX_LENGTH)
    codepath = models.CharField(max_length=FILEPATH_MAX_LENGTH)
    whiteboardpath = models.CharField(max_length=FILEPATH_MAX_LENGTH)
    chatpath = models.CharField(max_length=FILEPATH_MAX_LENGTH)
    def __str__(self):
        return self.name


class ExcelFile(models.Model):
    #name = models.CharField(max_length=NAME_MAX_LENGTH)
    file = models.FileField(upload_to=EXCEL_URL)


class HR(models.Model):
    user = models.OneToOneField(User)
    email = models.CharField(max_length=EMAIL_MAX_LENGTH)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    company = models.CharField(max_length=NAME_MAX_LENGTH)

