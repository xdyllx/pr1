# coding=utf-8
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.shortcuts import render
from Question.models import *
from HRRoomManagement.models import Interview, Interviewer, Candidate
import json
from django.template import Context, Template
from ink.settings import BASE_DIR
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import time
import re
import os
import sys
reload(sys)

TEMPLATE_DIR = BASE_DIR + "/templates/"
FILE_DIR = BASE_DIR + "/static/media/file/"


# （对题目的）操作名
ACTION = [u"添加", u"编辑", u"删除"]
ADD = 0
EDIT = 1
DEL = 2

# 四种题目
QUESTION_TYPE = [u"选择题", u"填空题", u"简答题", u"编程题"]
CHOICE = 0
COMPLETION = 1
ESSAY = 2
CODE = 3

# 题目操作异常信息
EMPTY_INPUT = u"输入必须非空！"
NO_BLANKS = u"填空题题干须含有【】或[]。"
TITLE_OVERFLOW = u"溢出（标题最大长度为" + str(TITLE_MAXLENGTH) + u"字）。"
STEM_OVERFLOW = u"溢出（题干最大长度为" + str(STEM_MAXLENGTH) + u"字）。"
COMPLETION_ANSWER_OVERFLOW = u"溢出（填空题答案最大长度为" + \
    str(COMPLETION_ANSWER_MAXLENGTH) + u"字）。"
ESSAY_ANSWER_OVERFLOW = u"溢出（填空题答案最大长度为" + str(ESSAY_ANSWER_MAXLENGTH) + u"字）。"
SAMPLE_OVERFLOW = u"溢出（编程题样例输入/输出最大长度为" + str(SAMPLE_MAXLENGTH) + u"字）。"
OPNUM_FEWER_THAN_TWO = u"选择题选项数目不得小于两个。"
ILLEGAL_ANSWER = u"选择题答案非法！"
REDUPLICATIVE_OPTIONS = u"选择题答案有重复！"
NO_SUCH_ID = u"数据库中不存在相应id的题目！"
REDUPLICATIVE_TITLE = u"题目标题出现重复！"
NO_OPTIONS_CHECKED = u"请至少选择一个选项作为答案！"

# 处理id前缀
CHOICE_PREFIX_LENGTH = 7
COMPLETION_PREFIX_LENGTH = 11
ESSAY_PREFIX_LENGTH = 6
CODE_PREFIX_LENGTH = 5

# API种类
CANDIDATE_JSEND = u"请求候选人列表"
QUESTION_JSEND = u"请求所有面试题"

# API异常信息
ROOM_ID_REQUIRED = u"url缺少房间id！"
NO_SUCH_ROOM_ID = u"数据库中不存在相应id的房间！"
ILLEGAL_ENCODED_ROOMID = u"房间号编码与房间信息不对应！"
ROOM_ID = 0


# 添加、编辑、删除4种题目时的异常
class Error(Exception):

    def __init__(self, action, questionType, message=u""):
        self.action = ACTION[action]
        self.questionType = QUESTION_TYPE[questionType]
        # self.errorInfo = self.action + " " + self.questionType
        if message != u"":
            # self.errorInfo = " 注意：" + message
            self.errorInfo = message


# 面试房间调用我们的API时出现的异常
class APIError(Exception):

    def __init__(self, APIType, message=u""):
        self.errorInfo = APIType
        if message != u"":
            self.errorInfo += ":" + message


# 网址中房间号参数非法
class RoomError(Exception):
    def __init__(self,  message=u""):
        if message != u"":
            self.errorInfo = message


# 返回成功信息
def getSuccessInfo(action, questionType):
    return ACTION[action] + QUESTION_TYPE[questionType] + u"成功！"


# 渲染所有选择题
def showChoice(request):
    roomId = int(request.GET.get('room').split("_")[1])
    page = getQuestionRender('choice', roomId)
    return HttpResponse(page)


# 渲染所有填空题
def showCompletion(request):
    roomId = int(request.GET.get('room').split("_")[1])
    page = getQuestionRender('completion', roomId)
    return HttpResponse(page)


# 渲染所有简答题
def showEssay(request):
    roomId = int(request.GET.get('room').split("_")[1])
    page = getQuestionRender('essay', roomId)
    return HttpResponse(page)


# 渲染所有编程题
def showCode(request):
    roomId = int(request.GET.get('room').split("_")[1])
    page = getQuestionRender('code', roomId)
    return HttpResponse(page)


# 渲染面试房间 候选人列表界面
def showInterviewee(request):
    candidateList = []
    roomId = int(request.GET.get('room').split("_")[1])
    candidates = Candidate.objects.all()
    for candidate in candidates:
        if candidate.interview.id == roomId:
            context = {}
            context['name'] = candidate.name
            context['phone'] = candidate.phoneNumber
            context['email'] = candidate.email
            context['state'] = candidate.state
            context['id'] = candidate.id
            candidateList.append(context)
    allTheText = open(TEMPLATE_DIR + "interviewee.html").read()
    theTemplate = Template(allTheText)
    theContext = Context({'candidateList': candidateList})
    theRenderPage = theTemplate.render(theContext)
    return HttpResponse(theRenderPage)


# 【API】给面试房间提供的题目Jsend中，选择题选项
def getOptionsInJsend(op):
    options = []
    opLetter = ["A", "B", "C", "D", "E", "F"]
    for i in range(0, 6):
        if op[i] != "":
            options.append(opLetter[i] + "." + op[i])
    return options


# 【API】给面试房间提供的题目Jsend中，选择题
def getChoiceListInJsend(roomID, mark):
    room = Interview.objects.filter(id=roomID)
    choices = Choice.objects.filter(interview=room)
    _mark = mark
    choiceList = []
    for choice in choices:
        context = {}
        body = {}
        op = [choice.optionA, choice.optionB, choice.optionC,
              choice.optionD, choice.optionE, choice.optionF]
        options = getOptionsInJsend(op)
        body['number'] = choice.id
        body['title'] = choice.title
        body['stem'] = choice.stem
        body['options'] = options
        body['answer'] = choice.answer
        context['id'] = _mark
        _mark += 1
        context['type'] = "choice"
        context['body'] = body
        choiceList.append(context)
    return {'choiceList': choiceList, 'mark': _mark}


# 【API】给面试房间提供的题目Jsend中，填空题
def getCompletionListInJsend(roomID, mark):
    room = Interview.objects.filter(id=roomID)
    completions = Completion.objects.filter(interview=room[0])
    _mark = mark
    completionList = []
    for completion in completions:
        context = {}
        body = {}
        body['number'] = completion.id
        body['title'] = completion.title
        body['stem'] = completion.stem
        body['answer'] = completion.answer
        context['id'] = _mark
        _mark += 1
        context['type'] = "completion"
        context['body'] = body
        completionList.append(context)
    return {'completionList': completionList, 'mark': _mark}


# 【API】给面试房间提供的题目Jsend中，简答题
def getEssayListInJsend(roomID, mark):
    room = Interview.objects.filter(id=roomID)
    essays = Essay.objects.filter(interview=room[0])
    _mark = mark
    essayList = []
    for essay in essays:
        context = {}
        body = {}
        body['number'] = essay.id
        body['title'] = essay.title
        body['stem'] = essay.stem
        body['answer'] = essay.answer
        context['id'] = _mark
        _mark += 1
        context['type'] = "essay"
        context['body'] = body
        essayList.append(context)
    return {'essayList': essayList, 'mark': _mark}


# 【API】给面试房间提供的题目Jsend中，编程题
def getCodeListInJsend(roomID, mark):
    room = Interview.objects.filter(id=roomID)
    codes = Code.objects.filter(interview=room[0])
    _mark = mark
    codeList = []
    for code in codes:
        context = {}
        body = {}
        body['number'] = code.id
        body['title'] = code.title
        body['stem'] = code.stem
        body['sampleInput'] = code.sampleInput
        body['sampleOutput'] = code.sampleOutput
        context['id'] = _mark
        _mark += 1
        context['type'] = "code"
        context['body'] = body
        codeList.append(context)
    return {'codeList': codeList, 'mark': _mark}


# 检查编码后的房间号是否合法，不合法时返回True
def checkIllegalEncodedRoomID(encodedRoomId):  # encodedRoomId是一个字符串
    if len(encodedRoomId.split("_")) != 2:
        return True
    roomId = int(encodedRoomId.split("_")[1])
    if checkIllegalRoomId(roomId):
        return True
    if getEncodedRoomID(roomId) == encodedRoomId:
        return False
    else:
        return True


# 生成根据面试官邮箱编码后的roomId
def getEncodedRoomID(roomId):  # roomId是整数，retId是一个字符串
    if checkIllegalRoomId(roomId):
        return "no_such_id"
    room = Interview.objects.filter(id=roomId)
    interviewer = Interviewer.objects.filter(interview=room[0])
    email = interviewer[0].email
    hash = BKDRHash(email)
    retId = str(hash) + "_" + str(roomId)
    return retId


# BKDR字符串hash算法
def BKDRHash(string):
    seed = 131
    hash = 0
    for i in range(0, len(string)):
        hash = hash * seed + ord(string[i])
    return hash & 0x7fffffff


# 【API】给面试房间提供的题目列表Jsend
def getQuestionJsend(request):
    retInfo = {}
    try:
        if request.GET.get('room') is None:  # 有待考证
            raise APIError(QUESTION_JSEND, ROOM_ID_REQUIRED)
        if checkIllegalEncodedRoomID(request.GET.get('room')):
            raise APIError(QUESTION_JSEND, ILLEGAL_ENCODED_ROOMID)
        roomID = int(request.GET.get('room').split("_")[1])
        if checkIllegalRoomId(roomID):
            raise APIError(QUESTION_JSEND, NO_SUCH_ROOM_ID)
        questionList = []
        choiceRet = getChoiceListInJsend(roomID, 1)
        choiceList = choiceRet['choiceList']
        completionRet = getCompletionListInJsend(roomID, choiceRet['mark'])
        completionList = completionRet['completionList']
        essayRet = getEssayListInJsend(roomID, completionRet['mark'])
        essayList = essayRet['essayList']
        codeRet = getCodeListInJsend(roomID, essayRet['mark'])
        codeList = codeRet['codeList']
        for elem in choiceList:
            questionList.append(elem)
        for elem in completionList:
            questionList.append(elem)
        for elem in essayList:
            questionList.append(elem)
        for elem in codeList:
            questionList.append(elem)
        retInfo['status'] = 'success'
        retInfo['data'] = {'posts': questionList}
        return HttpResponse(
            json.dumps(retInfo),
            content_type="application/json")
    except APIError as e:
        retInfo['status'] = 'fail'
        retInfo['data'] = {'title': e.errorInfo}
        return HttpResponse(
            json.dumps(retInfo),
            content_type="application/json")


# 【API】给面试房间提供的候选人列表Jsend
def getCandidateJsend(request):
    retInfo = {}
    try:
        if request.GET.get('room') is None:  # 有待考证
            raise APIError(CANDIDATE_JSEND, ROOM_ID_REQUIRED)
        if checkIllegalEncodedRoomID(request.GET.get('room')):
            raise APIError(CANDIDATE_JSEND, ILLEGAL_ENCODED_ROOMID)
        roomID = int(request.GET.get('room').split("_")[1])
        if checkIllegalRoomId(roomID):
            raise APIError(CANDIDATE_JSEND, NO_SUCH_ROOM_ID)
        retInfo['status'] = 'success'
        candidateList = []
        candidates = Candidate.objects.all()
        mark = 1
        for candidate in candidates:
            if candidate.interview.id == roomID:
                context = {}
                body = {}
                body['name'] = candidate.name
                body['id'] = candidate.id
                body['room'] = roomID
                context['body'] = body
                context['title'] = 'Candidate'
                context['id'] = mark
                mark += 1
                candidateList.append(context)
        retInfo['data'] = {'posts': candidateList}
        return HttpResponse(
            json.dumps(retInfo),
            content_type="application/json")
    except APIError as e:
        retInfo['status'] = 'fail'
        retInfo['data'] = {'title': e.errorInfo}
        return HttpResponse(
            json.dumps(retInfo),
            content_type="application/json")


# 【API】给面试房间提供的候选人列表Jsend
def getRoomJsend(request):
    retInfo = {}
    retInfo['status'] = 'success'
    roomList = []
    rooms = Interview.objects.all()
    for room in rooms:
        roomList.append(getEncodedRoomID(room.id))
    retInfo['data'] = {'posts': roomList}
    return HttpResponse(
        json.dumps(retInfo),
        content_type="application/json")


@csrf_exempt
# 渲染面试房间管理页面，包括该房间的题目和候选人列表
def showQuestions(request):
    try:
        if request.GET.get('room') is None:
            raise RoomError(ROOM_ID_REQUIRED)
        if checkIllegalEncodedRoomID(request.GET.get('room')):
            raise RoomError(ILLEGAL_ENCODED_ROOMID)
        if checkIllegalRoomId(request.GET.get('room').split("_")[1]):
            raise RoomError(NO_SUCH_ROOM_ID)
        return render(request, 'interviewerManage.html')
    except RoomError as e:
        return render(request, 'error.html')



# 返回某种题型的列表
def getQuestionList(type, roomId):
    questionList = []
    thisInterview = Interview.objects.filter(id=roomId)
    if type == 'choice':
        allChoices = Choice.objects.filter(interview=thisInterview)
        for item in allChoices:
            context = {}
            context['title'] = item.title
            context['type'] = 1
            context['id'] = 'choice_' + str(item.id)
            questionList.append(context)
    if type == 'completion':
        allCompletions = Completion.objects.filter(interview=thisInterview)
        for item in allCompletions:
            context = {}
            context['title'] = item.title
            context['type'] = 2
            context['id'] = 'completion_' + str(item.id)
            questionList.append(context)
    if type == 'essay':
        allEssays = Essay.objects.filter(interview=thisInterview)
        for item in allEssays:
            context = {}
            context['title'] = item.title
            context['type'] = 3
            context['id'] = 'essay_' + str(item.id)
            questionList.append(context)
    if type == 'code':
        allCodes = Code.objects.filter(interview=thisInterview)
        for item in allCodes:
            context = {}
            context['title'] = item.title
            context['type'] = 4
            context['id'] = 'code_' + str(item.id)
            questionList.append(context)
    return questionList


# 返回某种题型界面的渲染
def getQuestionRender(type, roomId):
    allTheText = open(TEMPLATE_DIR + type + ".html").read()
    theTemplate = Template(allTheText)
    theContext = Context({type + 'List': getQuestionList(type, roomId)})
    theRenderPage = theTemplate.render(theContext)
    return theRenderPage


# 房间Id非法时，返回True
def checkIllegalRoomId(roomId):
    room = Interview.objects.filter(id=roomId)
    if len(room) == 0:
        return True
    if len(room) == 1:
        return False


# 检查选择题选项是否为空
def checkOptionEmpty(op, opN):
    opNum = int(opN.encode('utf-8'))
    for i in range(0, opNum):
        if len(op[i]) == 0:
            return True
    return False


# 检查选择题答案是否非法（必须是大写A-F的子集，且与选项数目有关）
def checkIllegalAnswer(opN, answer):
    opNum = int(opN.encode('utf-8'))
    if ('C' in answer) and (opNum < 3):
        return True
    if ('D' in answer) and (opNum < 4):
        return True
    if ('E' in answer) and (opNum < 5):
        return True
    if ('F' in answer) and (opNum < 6):
        return True
    if not(
        'A' in answer) and not(
        'B' in answer) and not(
            'C' in answer) and not(
                'D' in answer) and not(
                    'E' in answer) and not(
                        'F' in answer):
        return True
    return False


# 检查选择题是否有选项相同
def checkReduplicativeOptions(op, opN):
    opNum = int(opN.encode('utf-8'))
    for i in range(0, opNum):
        for j in range(i + 1, opNum):
            if op[i] == op[j]:
                return True
    return False


# 在添加操作中，检查添加的新title是否与其他题目的title重名
def checkReduplicativeTitleInAdd(type, newTitle):
    question = []
    if type == 'choice':
        question += Choice.objects.filter(title=newTitle)
    if type == 'completion':
        question += Completion.objects.filter(title=newTitle)
    if type == 'essay':
        question += Essay.objects.filter(title=newTitle)
    if type == 'code':
        question += Code.objects.filter(title=newTitle)
    if len(question) != 0:
        return True
    return False


def innerAddChoice(title, stem, opA, opB, opC, opD,
                   opE, opF, opNum, answer, roomId):
    addChoiceInfo = {}
    op = [opA, opB, opC, opD, opE, opF]
    try:
        if checkIllegalRoomId(roomId):
            raise Error(ADD, CHOICE, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInAdd('choice', title):
            raise Error(ADD, CHOICE, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(ADD, CHOICE, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(ADD, CHOICE, STEM_OVERFLOW)
        if len(answer) == 0:
            raise Error(ADD, CHOICE, NO_OPTIONS_CHECKED)
        if len(title) == 0 or len(stem) == 0 or checkOptionEmpty(op, opNum):
            raise Error(ADD, CHOICE, EMPTY_INPUT)
        if int(opNum) < 2:
            raise Error(ADD, CHOICE, OPNUM_FEWER_THAN_TWO)
        if checkIllegalAnswer(opNum, answer):
            raise Error(ADD, CHOICE, ILLEGAL_ANSWER)
        if checkReduplicativeOptions(op, opNum):
            raise Error(ADD, CHOICE, REDUPLICATIVE_OPTIONS)
        room = Interview.objects.filter(id=roomId)
        choice = Choice.objects.create(
            title=title,
            stem=stem,
            optionA=opA,
            optionB=opB,
            optionC=opC,
            optionD=opD,
            optionE=opE,
            optionF=opF,
            optionNum=opNum,
            answer=answer,
            interview=room[0])
        choice.save()
        addChoiceInfo['status'] = 'success'
        addChoiceInfo['message'] = getSuccessInfo(ADD, CHOICE)
        return addChoiceInfo
    except Error as e:
        addChoiceInfo['status'] = 'fail'
        addChoiceInfo['message'] = e.errorInfo
        return addChoiceInfo


# 响应前端“添加选择题”
def addChoice(request):
    addChoiceInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['choiceTitle']
        theStem = request.POST['choiceStem']
        theOptionA = request.POST['A']
        theOptionB = request.POST['B']
        theOptionC = request.POST['C']
        theOptionD = request.POST['D']
        theOptionE = request.POST['E']
        theOptionF = request.POST['F']
        theOptionNum = request.POST['optionNum']
        theAnswer = request.POST['choiceAnswer']
        addChoiceInfo = innerAddChoice(
            theTitle,
            theStem,
            theOptionA,
            theOptionB,
            theOptionC,
            theOptionD,
            theOptionE,
            theOptionF,
            theOptionNum,
            theAnswer,
            roomId)
        addChoiceInfo['body'] = getQuestionRender('choice', roomId)
    return HttpResponse(
        json.dumps(addChoiceInfo),
        content_type="application/json")


def innerAddCompletion(title, stem, answer, roomId):
    addCompletionInfo = {}
    try:
        if checkIllegalRoomId(roomId):
            raise Error(ADD, COMPLETION, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInAdd('completion', title):
            raise Error(ADD, COMPLETION, REDUPLICATIVE_TITLE)
        zhPattern = re.compile(u'[\u3010][\u3011]')
        contents = stem
        match = zhPattern.search(contents)
        if not match and (not('[]' in stem)):
#        if (not('【】'.decode('utf-8') in stem)) and (not('[]' in stem)):
            raise Error(ADD, COMPLETION, NO_BLANKS)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(ADD, COMPLETION, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(ADD, COMPLETION, STEM_OVERFLOW)
        if len(answer) >= COMPLETION_ANSWER_MAXLENGTH:
            raise Error(ADD, COMPLETION, COMPLETION_ANSWER_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(answer) == 0:
            raise Error(ADD, COMPLETION, EMPTY_INPUT)
        room = Interview.objects.filter(id=roomId)
        completion = Completion.objects.create(
            title=title, stem=stem, answer=answer, interview=room[0])
        completion.save()
        addCompletionInfo['status'] = "success"
        addCompletionInfo['message'] = getSuccessInfo(ADD, COMPLETION)
        return addCompletionInfo
    except Error as e:
        addCompletionInfo['status'] = "fail"
        addCompletionInfo['message'] = e.errorInfo
        return addCompletionInfo


# 响应前端“添加填空题”
def addCompletion(request):
    addCompletionInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['completionTitle']
        theStem = request.POST['completionStem']
        theAnswer = request.POST['completionAnswer']
        addCompletionInfo = innerAddCompletion(
            theTitle, theStem, theAnswer, roomId)
        addCompletionInfo['body'] = getQuestionRender('completion', roomId)
    return HttpResponse(
        json.dumps(addCompletionInfo),
        content_type="application/json")


def innerAddEssay(title, stem, answer, roomId):
    addEssayInfo = {}
    try:
        if checkIllegalRoomId(roomId):
            raise Error(ADD, ESSAY, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInAdd('essay', title):
            raise Error(ADD, ESSAY, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(ADD, ESSAY, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(ADD, ESSAY, STEM_OVERFLOW)
        if len(answer) >= ESSAY_ANSWER_MAXLENGTH:
            raise Error(ADD, ESSAY, ESSAY_ANSWER_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(answer) == 0:
            raise Error(ADD, ESSAY, EMPTY_INPUT)
        room = Interview.objects.filter(id=roomId)
        essay = Essay.objects.create(
            title=title,
            stem=stem,
            answer=answer,
            interview=room[0])
        essay.save()
        addEssayInfo['status'] = 'success'
        addEssayInfo['message'] = getSuccessInfo(ADD, ESSAY)
        return addEssayInfo
    except Error as e:
        addEssayInfo['status'] = 'fail'
        addEssayInfo['message'] = e.errorInfo
        return addEssayInfo


# 响应前端“添加简答题”
def addEssay(request):
    addEssayInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['essayTitle']
        theStem = request.POST['essayStem']
        theAnswer = request.POST['essayAnswer']
        addEssayInfo = innerAddEssay(theTitle, theStem, theAnswer, roomId)
        addEssayInfo['body'] = getQuestionRender('essay', roomId)
    return HttpResponse(
        json.dumps(addEssayInfo),
        content_type="application/json")


def innerAddCode(title, stem, input, output, roomId):
    addCodeInfo = {}
    try:
        if checkIllegalRoomId(roomId):
            raise Error(ADD, CODE, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInAdd('code', title):
            raise Error(ADD, CODE, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(ADD, CODE, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(ADD, CODE, STEM_OVERFLOW)
        if (len(input) >= SAMPLE_MAXLENGTH) or (
                len(output) >= SAMPLE_MAXLENGTH):
            raise Error(ADD, CODE, SAMPLE_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(
                input) == 0 or len(output) == 0:
            raise Error(ADD, CODE, EMPTY_INPUT)
        room = Interview.objects.filter(id=roomId)
        code = Code.objects.create(
            title=title,
            stem=stem,
            sampleInput=input,
            sampleOutput=output,
            interview=room[0])
        code.save()
        addCodeInfo['status'] = 'success'
        addCodeInfo['message'] = getSuccessInfo(ADD, CODE)
        return addCodeInfo
    except Error as e:
        addCodeInfo['status'] = 'fail'
        addCodeInfo['message'] = e.errorInfo
        return addCodeInfo


# 响应前端“添加编程题”
def addCode(request):
    addCodeInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['codeTitle']
        theStem = request.POST['codeStem']
        theSampleInput = request.POST['codeSampleInput']
        theSampleOutput = request.POST['codeSampleOutput']
        addCodeInfo = innerAddCode(
            theTitle,
            theStem,
            theSampleInput,
            theSampleOutput,
            roomId)
        addCodeInfo['body'] = getQuestionRender('code', roomId)
    return HttpResponse(
        json.dumps(addCodeInfo),
        content_type="application/json")


# 在编辑操作中，检查编辑后的新title是否与其他题目的title重名
def checkReduplicativeTitleInEdit(type, newTitle, theId):
    oldQuestion = []
    reduplicativeQuestion = []
    if type == 'choice':
        oldQuestion += Choice.objects.filter(id=theId)
    if type == 'completion':
        oldQuestion += Completion.objects.filter(id=theId)
    if type == 'essay':
        oldQuestion += Essay.objects.filter(id=theId)
    if type == 'code':
        oldQuestion += Code.objects.filter(id=theId)
    oldTitle = oldQuestion[0].title
    if oldTitle != newTitle:    # 对于theId的这道题，如果编辑后的title不与之前一致，则需检查它是否与其他题的标题重复
        if type == 'choice':
            reduplicativeQuestion += Choice.objects.filter(title=newTitle)
        if type == 'completion':
            reduplicativeQuestion += Completion.objects.filter(title=newTitle)
        if type == 'essay':
            reduplicativeQuestion += Essay.objects.filter(title=newTitle)
        if type == 'code':
            reduplicativeQuestion += Code.objects.filter(title=newTitle)
        if len(reduplicativeQuestion) != 0:  # 如果重复，则返回True
            return True
    return False


# 保存编辑时，对该题目在media下的相关图片文件进行更新
def updateMediaImages(originStem, newStem):
    originImgurls = getImgUrlsInRichText(originStem)
    newImgurls = getImgUrlsInRichText(newStem)
    for oldurl in originImgurls:
        if not(oldurl in newImgurls) and os.path.exists(oldurl):
            os.remove(oldurl)


def innerEditChoice(
        title, stem,
        opA, opB, opC, opD, opE, opF, opNum,
        answer, editId, roomId):
    editChoiceInfo = {}
    op = [opA, opB, opC, opD, opE, opF]
    theId = int(editId[CHOICE_PREFIX_LENGTH:])
    try:
        if checkIllegalRoomId(roomId):
            raise Error(EDIT, CHOICE, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInEdit('choice', title, theId):
            raise Error(EDIT, CHOICE, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(EDIT, CHOICE, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(EDIT, CHOICE, STEM_OVERFLOW)
        if len(answer) == 0:
            raise Error(ADD, CHOICE, NO_OPTIONS_CHECKED)
        if len(title) == 0 or len(stem) == 0 or checkOptionEmpty(op, opNum):
            raise Error(ADD, CHOICE, EMPTY_INPUT)
        if int(opNum) < 2:
            raise Error(EDIT, CHOICE, OPNUM_FEWER_THAN_TWO)
        if checkIllegalAnswer(opNum, answer):
            raise Error(EDIT, CHOICE, ILLEGAL_ANSWER)
        if checkReduplicativeOptions(op, opNum):
            raise Error(EDIT, CHOICE, REDUPLICATIVE_OPTIONS)
        choice = Choice.objects.filter(id=theId)
        if len(choice) == 0:
            raise Error(EDIT, CHOICE, NO_SUCH_ID)
        if len(choice) == 1:
            choice[0].title = title
            updateMediaImages(choice[0].stem, stem)
            choice[0].stem = stem
            choice[0].optionA = opA
            choice[0].optionB = opB
            choice[0].optionC = opC
            choice[0].optionD = opD
            choice[0].optionE = opE
            choice[0].optionF = opF
            choice[0].optionNum = opNum
            choice[0].answer = answer
            choice[0].save()
            editChoiceInfo['status'] = 'success'
            editChoiceInfo['message'] = getSuccessInfo(EDIT, CHOICE)
            return editChoiceInfo
    except Error as e:
        editChoiceInfo['status'] = 'fail'
        editChoiceInfo['message'] = e.errorInfo
        return editChoiceInfo


# 响应前端“编辑选择题”
def editChoice(request):
    editChoiceInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['choiceTitle']
        theStem = request.POST['choiceStem']
        theOptionA = request.POST['A']
        theOptionB = request.POST['B']
        theOptionC = request.POST['C']
        theOptionD = request.POST['D']
        theOptionE = request.POST['E']
        theOptionF = request.POST['F']
        theOptionNum = request.POST['optionNum']
        theAnswer = request.POST['choiceAnswer']
        editId = request.POST['choiceId']
        editChoiceInfo = innerEditChoice(
            theTitle,
            theStem,
            theOptionA,
            theOptionB,
            theOptionC,
            theOptionD,
            theOptionE,
            theOptionF,
            theOptionNum,
            theAnswer,
            editId,
            roomId)
        editChoiceInfo['body'] = getQuestionRender('choice', roomId)
    return HttpResponse(
        json.dumps(editChoiceInfo),
        content_type="application/json")


def innerEditCompletion(title, stem, answer, editId, roomId):
    editCompletionInfo = {}
    theId = int(editId[COMPLETION_PREFIX_LENGTH:])
    try:
        if checkIllegalRoomId(roomId):
            raise Error(EDIT, COMPLETION, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInEdit('completion', title, theId):
            raise Error(EDIT, COMPLETION, REDUPLICATIVE_TITLE)
	zhPattern = re.compile(u'[\u3010][\u3011]')
        contents = stem
        match = zhPattern.search(contents)
        if not match and (not('[]' in stem)):
	#if (not('【】'.decode('utf-8') in stem)) and (not('[]' in stem)):
            raise Error(EDIT, COMPLETION, NO_BLANKS)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(EDIT, COMPLETION, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(EDIT, COMPLETION, STEM_OVERFLOW)
        if len(answer) >= COMPLETION_ANSWER_MAXLENGTH:
            raise Error(EDIT, COMPLETION, COMPLETION_ANSWER_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(answer) == 0:
            raise Error(EDIT, COMPLETION, EMPTY_INPUT)
        completion = Completion.objects.filter(id=theId)
        if len(completion) == 0:
            raise Error(EDIT, COMPLETION, NO_SUCH_ID)
        if len(completion) == 1:
            completion[0].title = title
            updateMediaImages(completion[0].stem, stem)
            completion[0].stem = stem
            completion[0].answer = answer
            completion[0].save()
            editCompletionInfo['status'] = 'success'
            editCompletionInfo['message'] = getSuccessInfo(EDIT, COMPLETION)
            return editCompletionInfo
    except Error as e:
        editCompletionInfo['status'] = 'fail'
        editCompletionInfo['message'] = e.errorInfo
        return editCompletionInfo


# 响应前端“编辑填空题”
def editCompletion(request):
    editCompletionInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['completionTitle']
        theStem = request.POST['completionStem']
        theAnswer = request.POST['completionAnswer']
        editId = request.POST['completionId']
        editCompletionInfo = innerEditCompletion(
            theTitle, theStem, theAnswer, editId, roomId)
        editCompletionInfo['body'] = getQuestionRender('completion', roomId)
    return HttpResponse(
        json.dumps(editCompletionInfo),
        content_type="application/json")


def innerEditEssay(title, stem, answer, editId, roomId):
    editEssayInfo = {}
    theId = int(editId[ESSAY_PREFIX_LENGTH:])
    try:
        if checkIllegalRoomId(roomId):
            raise Error(EDIT, ESSAY, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInEdit('essay', title, theId):
            raise Error(EDIT, ESSAY, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(EDIT, ESSAY, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(EDIT, ESSAY, STEM_OVERFLOW)
        if len(answer) >= ESSAY_ANSWER_MAXLENGTH:
            raise Error(EDIT, ESSAY, ESSAY_ANSWER_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(answer) == 0:
            raise Error(EDIT, ESSAY, EMPTY_INPUT)
        essay = Essay.objects.filter(id=theId)
        if len(essay) == 0:
            raise Error(EDIT, ESSAY, NO_SUCH_ID)
        if len(essay) == 1:
            essay[0].title = title
            updateMediaImages(essay[0].stem, stem)
            essay[0].stem = stem
            essay[0].answer = answer
            essay[0].save()
            editEssayInfo['status'] = 'success'
            editEssayInfo['message'] = getSuccessInfo(EDIT, ESSAY)
            return editEssayInfo
    except Error as e:
        editEssayInfo['status'] = 'fail'
        editEssayInfo['message'] = e.errorInfo
        return editEssayInfo


# 响应前端“编辑简答题”
def editEssay(request):
    editEssayInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['essayTitle']
        theStem = request.POST['essayStem']
        theAnswer = request.POST['essayAnswer']
        editId = request.POST['essayId']
        editEssayInfo = innerEditEssay(
            theTitle, theStem, theAnswer, editId, roomId)
        editEssayInfo['body'] = getQuestionRender('essay', roomId)
    return HttpResponse(
        json.dumps(editEssayInfo),
        content_type="application/json")


def innerEditCode(title, stem, input, output, editId, roomId):
    editCodeInfo = {}
    theId = int(editId[CODE_PREFIX_LENGTH:])
    try:
        if checkIllegalRoomId(roomId):
            raise Error(EDIT, ESSAY, NO_SUCH_ROOM_ID)
        if checkReduplicativeTitleInEdit('code', title, theId):
            raise Error(EDIT, CODE, REDUPLICATIVE_TITLE)
        if len(title) >= TITLE_MAXLENGTH:
            raise Error(EDIT, CODE, TITLE_OVERFLOW)
        if len(stem) >= STEM_MAXLENGTH:
            raise Error(EDIT, CODE, STEM_OVERFLOW)
        if (len(input) >= SAMPLE_MAXLENGTH) or (
                len(output) >= SAMPLE_MAXLENGTH):
            raise Error(EDIT, CODE, SAMPLE_OVERFLOW)
        if len(title) == 0 or len(stem) == 0 or len(
                input) == 0 or len(output) == 0:
            raise Error(EDIT, CODE, EMPTY_INPUT)
        code = Code.objects.filter(id=theId)
        if len(code) == 0:
            raise Error(EDIT, CODE, NO_SUCH_ID)
        if len(code) == 1:
            code[0].title = title
            updateMediaImages(code[0].stem, stem)
            code[0].stem = stem
            code[0].sampleInput = input
            code[0].sampleOutput = output
            code[0].save()
            editCodeInfo['status'] = 'success'
            editCodeInfo['message'] = getSuccessInfo(EDIT, CODE)
            return editCodeInfo
    except Error as e:
        editCodeInfo['status'] = 'fail'
        editCodeInfo['message'] = e.errorInfo
        return editCodeInfo


# 响应前端“编辑编程题”
def editCode(request):
    editCodeInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        theTitle = request.POST['codeTitle']
        theStem = request.POST['codeStem']
        theSampleInput = request.POST['codeSampleInput']
        theSampleOutput = request.POST['codeSampleOutput']
        editId = request.POST['codeId']
        editCodeInfo = innerEditCode(
            theTitle,
            theStem,
            theSampleInput,
            theSampleOutput,
            editId,
            roomId)
        editCodeInfo['body'] = getQuestionRender('code', roomId)
    return HttpResponse(
        json.dumps(editCodeInfo),
        content_type="application/json")


def getImgUrlsInRichText(stem):
    pattern = re.compile(r'src=\"[\w|\s|/|\.]*\"')
    result = re.findall(pattern, stem)
    imgurls = []
    if len(result) != 0:
        for item in result:
            imgurl = item[5:-1]  # 只截取url段
            imgurl = BASE_DIR + imgurl
            imgurls.append(imgurl)
    return imgurls


# 在题目被删除时，删除static/media下的相应图片
def delMediaImages(stem):
    imgurls = getImgUrlsInRichText(stem)
    for imgurl in imgurls:
        if os.path.exists(imgurl):
            os.remove(imgurl)


# 对不同题型type，删除数据库中id为delId的元素（或抛出异常）
def innerDel(type, delId, roomId):
    delInfo = {}
    try:    # 由于python"外层局部变量不好赋值"的特点，这里用append、+=来实现赋值，实际上只可能采取4个if中的一种来赋值
        theId = 0
        hasTheId = 0
        typeCard = 0
        allQuestions = []
        if type == 'choice':
            typeCard += CHOICE
            theId += int(delId[CHOICE_PREFIX_LENGTH:])
            allQuestions += Choice.objects.all()
        if type == 'completion':
            typeCard += COMPLETION
            theId += int(delId[COMPLETION_PREFIX_LENGTH:])
            allQuestions += Completion.objects.all()
        if type == 'essay':
            typeCard += ESSAY
            theId += int(delId[ESSAY_PREFIX_LENGTH:])
            allQuestions += Essay.objects.all()
        if type == 'code':
            typeCard += CODE
            theId += int(delId[CODE_PREFIX_LENGTH:])
            allQuestions += Code.objects.all()
        if checkIllegalRoomId(roomId):
            raise Error(DEL, typeCard, NO_SUCH_ROOM_ID)
        for question in allQuestions:
            if question.id == theId:
                delMediaImages(question.stem)
                question.delete()
                hasTheId += 1
                break
        if hasTheId == 0:
            raise Error(DEL, typeCard, NO_SUCH_ID)
        delInfo['status'] = 'success'
        delInfo['message'] = getSuccessInfo(DEL, typeCard)
        return delInfo
    except Error as e:
        delInfo['status'] = 'fail'
        delInfo['message'] = e.errorInfo
        return delInfo


# 响应前端“删除选择题”
def delChoice(request):
    delChoiceInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        delId = request.POST['id']
        delChoiceInfo = innerDel('choice', delId, roomId)  # 这里delId是一个字符串
        delChoiceInfo['body'] = getQuestionRender('choice', roomId)
    return HttpResponse(
        json.dumps(delChoiceInfo),
        content_type="application/json")


# 响应前端“删除填空题”
def delCompletion(request):
    delCompletionInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        delId = request.POST['id']
        delCompletionInfo = innerDel(
            'completion', delId, roomId)  # 这里delId是一个字符串
        delCompletionInfo['body'] = getQuestionRender('completion', roomId)
    return HttpResponse(
        json.dumps(delCompletionInfo),
        content_type="application/json")


# 响应前端“删除简答题”
def delEssay(request):
    delEssayInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        delId = request.POST['id']
        delEssayInfo = innerDel('essay', delId, roomId)  # 这里delId是一个字符串
        delEssayInfo['body'] = getQuestionRender('essay', roomId)
    return HttpResponse(
        json.dumps(delEssayInfo),
        content_type="application/json")


# 响应前端“删除编程题”
def delCode(request):
    delCodeInfo = {}
    roomId = int(request.GET.get('room').split("_")[1])
    if request.method == "POST":
        delId = request.POST['id']
        delCodeInfo = innerDel('code', delId, roomId)  # 这里delId是一个字符串
        delCodeInfo['body'] = getQuestionRender('code', roomId)
    return HttpResponse(
        json.dumps(delCodeInfo),
        content_type="application/json")


# “编辑选择题”前传数据给模态框
@csrf_exempt
def getChoiceById(request):
    choiceId = request.POST['choiceId']
    theId = int(choiceId[CHOICE_PREFIX_LENGTH:])
    dict = {}
    allChoices = Choice.objects.all()
    for item in allChoices:
        if item.id == theId:
            dict['title'] = item.title
            dict['stem'] = item.stem
            dict['optionA'] = item.optionA
            dict['optionB'] = item.optionB
            dict['optionC'] = item.optionC
            dict['optionD'] = item.optionD
            dict['optionE'] = item.optionE
            dict['optionF'] = item.optionF
            dict['answer'] = item.answer
            break
    return HttpResponse(json.dumps(dict), content_type="application/json")


# “编辑填空题”前传数据给模态框
def getCompletionById(request):
    completionId = request.GET['completionId']
    theId = int(completionId[COMPLETION_PREFIX_LENGTH:])
    dict = {}
    allCompletions = Completion.objects.all()
    for item in allCompletions:
        if item.id == theId:
            dict['title'] = item.title
            dict['stem'] = item.stem
            dict['answer'] = item.answer
            break
    return HttpResponse(json.dumps(dict), content_type="application/json")


# “编辑简答题”前传数据给模态框
def getEssayById(request):
    essayId = request.GET['essayId']
    theId = int(essayId[ESSAY_PREFIX_LENGTH:])
    dict = {}
    allEssays = Essay.objects.all()
    for item in allEssays:
        if item.id == theId:
            dict['title'] = item.title
            dict['stem'] = item.stem
            dict['answer'] = item.answer
            break
    return HttpResponse(json.dumps(dict), content_type="application/json")


# “编辑编程题”前传数据给模态框
def getCodeById(request):
    codeId = request.GET['codeId']
    theId = int(codeId[CODE_PREFIX_LENGTH:])
    dict = {}
    allCodes = Code.objects.all()
    for item in allCodes:
        if item.id == theId:
            dict['title'] = item.title
            dict['stem'] = item.stem
            dict['sampleInput'] = item.sampleInput
            dict['sampleOutput'] = item.sampleOutput
            break
    return HttpResponse(json.dumps(dict), content_type="application/json")


# 读（大）文件，返回文件内容
def readFile(filename, buf_size=8192):
    if not os.path.exists(filename):
        return
    with open(filename, "rb") as f:
        while True:
            content = f.read(buf_size)
            if content:
                yield content
            else:
                break


# 富文本上载图片
@csrf_exempt
def fileUpload(request):
    files = request.FILES.get('upload_file')  # 得到文件对象
    pattern = re.compile(r'.jpg|.png|.jpeg|.CR2|.bmp|.gif', re.I)
    if (files is None) or (len(re.findall(pattern, files.name)) == 0):  # 非图片格式
        upload_info = {
            "success": False,
            'file_path': 'illegal_file_path'}
        return HttpResponse(upload_info, content_type="application/json")
    else:
        fileDir = settings.MEDIA_ROOT
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        filenamePrefix = str(int(time.time())) + "_"
        filename = filenamePrefix + files.name
        filePath = fileDir + "richTextImg/" + filename
        open(filePath, 'wb+').write(files.read())  # 上传文件
        upload_info = {
            "success": True,
            'file_path': "/home/locke/ink/pr1/static/media/richTextImg/" + filename}
        upload_info = json.dumps(upload_info)  # 得到JSON格式的返回值
    return HttpResponse(upload_info, content_type="application/json")


# 面试结束后，面试房间传给我们候选人的面试状态（1：通过，2：未通过）

def getStatusAfterInterview(request):
    candidateId = int(request.GET['candidate'])
    status = int(request.GET['status'])
    cs = Candidate.objects.all()
    for item in cs:
        if item.id == candidateId:
            item.state = status
            item.save()
    return HttpResponse('success')

# 面试结束后，面试房间传给我们候选人5个面试文件的路径

def getFilepathAfterInterview(request):
    candidateId = int(request.GET['candidate'])
    cs = Candidate.objects.all()
    for item in cs:
        if item.id == candidateId:
            item.videopath = request.GET['videopath']
            item.reportpath = request.GET['reportpath']
            item.codepath = request.GET['codepath']
            item.whiteboardpath = request.GET['whiteboardpath']
            item.chatpath = request.GET['chatpath']
            item.save()

    return HttpResponse('success')

def checkVideoFilepath(request):
    candidateId = int(request.GET['intervieweeId'])
    dict = {}
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].videopath

    if os.path.exists(filepath):
        dict['status'] = "success"
        dict['message'] = u"面试视频已生成！"
    else:
        dict['status'] = "fail"
        dict['message'] = u"面试视频尚未生成！"
    return HttpResponse(json.dumps(dict), content_type="application/json")


def downloadVideo(request):
    candidateId = int(request.GET['intervieweeId'])
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].videopath
    filename = "video.wav"
    data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response


def checkReportFilepath(request):
    candidateId = int(request.GET['intervieweeId'])
    dict = {}
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].reportpath

    if os.path.exists(filepath):
        dict['status'] = "success"
        dict['message'] = u"面试报告已生成！"
    else:
        dict['status'] = "fail"
        dict['message'] = u"面试报告尚未生成！"
    return HttpResponse(json.dumps(dict), content_type="application/json")


def downloadReport(request):
    candidateId = int(request.GET['intervieweeId'])
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].reportpath
    filename = "report.txt"
    data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response


def checkFinalcodeFilepath(request):
    candidateId = int(request.GET['intervieweeId'])
    dict = {}
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].reportpath
    if os.path.exists(filepath):
        dict['status'] = "success"
        dict['message'] = u"代码记录已生成！"
    else:
        dict['status'] = "fail"
        dict['message'] = u"代码记录尚未生成！"
    return HttpResponse(json.dumps(dict), content_type="application/json")


def downloadFinalcode(request):
    candidateId = int(request.GET['intervieweeId'])
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].codepath
    filename = "final_code.html"
    data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response


def checkWhiteboardFilepath(request):
    candidateId = int(request.GET['intervieweeId'])
    dict = {}
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].reportpath
    if os.path.exists(filepath):
        dict['status'] = "success"
        dict['message'] = u"白板记录已生成！"
    else:
        dict['status'] = "fail"
        dict['message'] = u"白板记录尚未生成！"
    return HttpResponse(json.dumps(dict), content_type="application/json")


def downloadWhiteboard(request):
    candidateId = int(request.GET['intervieweeId'])
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].whiteboardpath
    filename = "whiteboard_record.html"
    data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response


def checkChatFilepath(request):
    candidateId = int(request.GET['intervieweeId'])
    dict = {}
    candidate = Candidate.objects.filter(id=candidateId)
    status = candidate[0].state
    if status != 0:
        dict['status'] = "success"
        dict['message'] = u"聊天记录已生成！"
    else:
        dict['status'] = "fail"
        dict['message'] = u"聊天记录尚未生成！"
    print candidateId
    print candidate[0].chatpath
    return HttpResponse(json.dumps(dict), content_type="application/json")



def downloadChat(request):
    candidateId = int(request.GET['intervieweeId'])
    candidate = Candidate.objects.filter(id=candidateId)
    filepath = candidate[0].chatpath
    filename = "chat_record.txt"
    data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response

