#coding=utf-8

from django.db import models
import django.utils.timezone as timezone
from HRRoomManagement.models import Interview
# from froala_editor.fields import FroalaField

TITLE_MAXLENGTH = 50
STEM_MAXLENGTH = 500
OPTION_MAXLENGTH = 50
DEFAULT_OPTIONNUM = 6
MAX_OPTIONSNUM = 7
COMPLETION_ANSWER_MAXLENGTH = 100
ESSAY_ANSWER_MAXLENGTH = 300
SAMPLE_MAXLENGTH = 400


# 候选人model
class Choice(models.Model):

    title = models.CharField(max_length=TITLE_MAXLENGTH)  # 标题
    stem = models.CharField(max_length=STEM_MAXLENGTH)  # 题干
    optionA = models.CharField(max_length=OPTION_MAXLENGTH)
    optionB = models.CharField(max_length=OPTION_MAXLENGTH)
    optionC = models.CharField(max_length=OPTION_MAXLENGTH)
    optionD = models.CharField(max_length=OPTION_MAXLENGTH)
    optionE = models.CharField(max_length=OPTION_MAXLENGTH)
    optionF = models.CharField(max_length=OPTION_MAXLENGTH)
    optionNum = models.IntegerField(default=DEFAULT_OPTIONNUM)
    answer = models.CharField(max_length=MAX_OPTIONSNUM)  # "A", "ABD", etc.
    interview = models.ForeignKey(Interview)

    def __str__(self):
        return self.title


class Completion(models.Model):

    title = models.CharField(max_length=TITLE_MAXLENGTH)  # 标题
    stem = models.CharField(max_length=STEM_MAXLENGTH)  # 题干
    answer = models.CharField(max_length=COMPLETION_ANSWER_MAXLENGTH)
    interview = models.ForeignKey(Interview)

    def __str__(self):
        return self.title


class Essay(models.Model):

    title = models.CharField(max_length=TITLE_MAXLENGTH)  # 标题
    stem = models.CharField(max_length=STEM_MAXLENGTH)  # 题干
    answer = models.CharField(max_length=ESSAY_ANSWER_MAXLENGTH)
    interview = models.ForeignKey(Interview)

    def __str__(self):
        return self.title


class Code(models.Model):

    title = models.CharField(max_length=TITLE_MAXLENGTH)  # 标题
    stem = models.CharField(max_length=STEM_MAXLENGTH)  # 题干
    sampleInput = models.CharField(max_length=SAMPLE_MAXLENGTH)
    sampleOutput = models.CharField(max_length=SAMPLE_MAXLENGTH)
    interview = models.ForeignKey(Interview)

    def __str__(self):
        return self.title