# coding=utf-8
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import Template, Context
from django.core.mail import send_mail
from models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# import socket
from ink.settings import EMAIL_HOST_USER, BASE_DIR, ALLOWED_HOSTS
import xlrd
import re
import os
import json
TEMPLATE_DIR = BASE_DIR + '/templates/'


# socket.getaddrinfo('127.0.0.1', 8080)
emailForm = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
phoneNumberForm = r'^[1][3,4,5,7,8][0-9]{9}$'
timeForm = r'^(\d{4})-(0\d{1}|1[0-2])-(0\d{1}|[12]\d{1}|3[01])\s+(0\d{1}|1\d{1}|2[0-3]):([0-5]\d{1})$'
imagePattern = re.compile(r'.jpg|.png|.jpeg|.bmp', re.I)
excelPattern = re.compile(r'.xlsx|.xls', re.I)

# ERROR PARAMETERS
CLASSTYPE = [u'面试房间', u'面试官', u'候选人', u'HR']
ROOM = 0
INTERVIEWER = 1
CANDIDATE = 2
HRMANAGER = 3
ACTION = [u'添加', u'编辑', u'删除']
ADD = 0
EDIT = 1
DELETE = 2
NOT_EMPTY = u'输入不能为空'
NAME_TOO_LONG = u'内容过长'
EMAIL_FORM_ERROR = u'邮箱格式错误'
TIME_FORM_ERROR = u'时间格式错误'
SAME_NAME_ERROR = u'房间名称不能重复'
FILE_FORM_ERROR = u'文件格式错误'
PHONENUMBER_FORM_ERROR = u'手机号码格式错误'
ROOM_NOT_EXIST = u'房间不存在'
CANDIDATE_NOT_EXIST = u'候选人不存在'
verification = ['l6fwi', 'fmzjj', 'npzvh', 'uwntg', 'ji1ke',
                'p2vaz', 'uoxro', 'spffr', '4ksua', 'qtdbf']


class Error(Exception):

    def __init__(self, action, classtype, message=u''):
        # self.errorInfo = u'操作失败:' + ACTION[action] + CLASSTYPE[classtype]
        self.errorInfo = message


def enterLogin(request):
    return HttpResponseRedirect('/ink/login/')
    # return render(request, 'login.html')


def getHRManageRender():
    all_the_text = open(TEMPLATE_DIR + 'HRManage.html').read()
    pageTemplate = Template(all_the_text)
    # pageContext = Context({'candidateList': getAllCandidate(), 'roomList': getRoomList()})
    pageText = pageTemplate.render(Context())
    return pageText


def getRoomManageRender():
    all_the_text = open(TEMPLATE_DIR + 'roomManage.html').read()
    pageTemplate = Template(all_the_text)
    roomList = getRoomList()
    pageContext = Context({'roomNumber': len(roomList), 'roomList': roomList})
    pageText = pageTemplate.render(pageContext)
    return pageText


def getCandidateManageRender():
    all_the_text = open(TEMPLATE_DIR + 'candidateManage.html').read()
    pageTemplate = Template(all_the_text)
    haveCandidate = len(Candidate.objects.all())
    pageContext = Context({'candidateList': getAllCandidate(
    ), 'roomList': getRoomList(), 'haveCandidate': haveCandidate})
    pageText = pageTemplate.render(pageContext)
    return pageText


@login_required
def showHRManage(request):
    # pageText = getHRManageRender()
    # return HttpResponse(pageText)
    username = str(request.user)
    return render(request, 'HRManage.html', {'username': username})


@login_required
def roomManage(request):
    # pageText = getRoomManageRender()
    # return HttpResponse(pageText)
    roomList = getRoomList()
    return render(
        request, 'roomManage.html', {
            'roomNumber': len(roomList), 'roomList': roomList})


@login_required
def candidateManage(request):
    pageText = getCandidateManageRender()
    return HttpResponse(pageText)
    # return render(request, 'candidateManage.html', {'candidateList':
    # getAllCandidate(), 'roomList': getRoomList()})


def getRoomList():
    allInterviews = Interview.objects.all()
    roomList = []
    for item in allInterviews:
        context = {}
        context['roomname'] = item.name
        interviewer = Interviewer.objects.get(interview=item)
        context['interviewername'] = interviewer.name
        context['email'] = interviewer.email
        context['starttime'] = item.startTime
        context['id'] = item.id
        context['logo'] = item.logo
        candidates = Candidate.objects.filter(interview=item)
        context['candidateNumber'] = len(candidates)
        roomList.append(context)
    return roomList

# 函数功能:获得一个面试房间下的候选人列表
# 参数：房间的id


def getCandidateListOfRoom(roomid):
    interview = Interview.objects.get(id=roomid)
    candidates = Candidate.objects.filter(interview=interview)
    candList = []
    for candidate in candidates:
        context = {}
        context['candidateName'] = candidate.name
        context['phoneNumber'] = candidate.phoneNumber
        context['email'] = candidate.email
        context['roomName'] = candidate.interview.name
        context['state'] = candidate.state
        context['id'] = candidate.id
        candList.append(context)
    return candList


def getAllCandidate():
    candidateList = []
    allInterview = Interview.objects.all()
    for intw in allInterview:
        context = {}
        context['name'] = intw.name
        context['candList'] = getCandidateListOfRoom(intw.id)
        context['listLength'] = len(context['candList'])
        candidateList.append(context)
    return candidateList


# def getCandidateListinOnePage(page):
#     candidateList = getAllCandidate()

# 响应前端“添加房间”
@login_required
@csrf_exempt
def addRoom(request):
    if request.method == 'POST':
        roomName = request.POST['roomName']
        starttime = request.POST['starttime']
        logo = request.FILES.get('addRoom_logoInput')

        interviewerName = request.POST['interviewerName']
        interviewerEmail = request.POST['interviewerEmail']
        data = innerCreateRoom(
            roomName,
            starttime,
            logo,
            interviewerName,
            interviewerEmail)
        pageText = getRoomManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')

# 响应前端“删除房间”


@login_required
def delRoom(request):
    if request.POST:
        id = request.POST['id']
        data = innerDeleteRoom(id)
        pageText = getRoomManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')


# 响应前端“编辑房间”
@login_required
@csrf_exempt
def editRoom(request):
    if request.POST:
        roomName = request.POST['roomName']
        startTime = request.POST['interviewStartTime']
        logo = request.FILES.get('editRoom_logoInput')

        id = request.POST['id']
        interviewerName = request.POST['interviewerName']
        interviewerEmail = request.POST['interviewerEmail']
        data = innerEditRoom(
            roomName,
            startTime,
            logo,
            interviewerName,
            interviewerEmail,
            id)
        pageText = getRoomManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')


# 向面试官发送邮件
@login_required
def sendEmailToInterviewer(request):
    data = {}
    if request.POST:
        subject = request.POST['roomName']
        receiverEmail = request.POST['interviewerEmail']
        context = request.POST['emailContext']
        try:
            send_mail(
                subject,
                context,
                EMAIL_HOST_USER,
                [receiverEmail],
                fail_silently=False)
            data['status'] = 'success'
        except:
            data['status'] = 'fail'
            data['message'] = '发送邮件异常'
    pageText = getRoomManageRender()
    data['pageText'] = pageText
    return HttpResponse(json.dumps(data), content_type='application/json')


# 向候选人发送邮件
@login_required
def sendEmailToCandidate(request):
    data = {}
    if request.POST:
        subject = request.POST['candidateName']
        receiverEmail = request.POST['candidateEmail']
        context = request.POST['emailContext']
        try:
            send_mail(
                subject,
                context,
                EMAIL_HOST_USER,
                [receiverEmail],
                fail_silently=False)
            data['status'] = 'success'
        except:
            data['status'] = 'fail'
            data['message'] = '发送邮件异常'

    pageText = getCandidateManageRender()
    data['pageText'] = pageText
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def getInterviewerURL(request):
    roomId = 1
    interviewerId = request.GET['interviewerId']
    interviewers = Interviewer.objects.all()
    for interviewer in interviewers:
        if str(interviewer.id) == interviewerId:
            roomId = interviewer.interview.id
            break
    url = 'http://' + ALLOWED_HOSTS[0] + ':8000/ink/interviewerManage?room=' + \
         getEncodedRoomID(roomId)
    return HttpResponse(url)


@login_required
def getCandidateURL(request):
    roomId = 1
    candidateId = request.GET['candidateId']
    candidates = Candidate.objects.all()
    for candidate in candidates:
        if str(candidate.id) == candidateId:
            roomId = candidate.interview.id
            break
    url = 'http://' + ALLOWED_HOSTS[0] + ':8000/ink/candidate?room=' + \
         getEncodedRoomID(roomId) + "&id=" + candidateId
    return HttpResponse(url)


# 响应前端“添加候选人”
@login_required
def addCandidate(request):
    if request.POST:
        candidateName = request.POST['candidateName']
        email = request.POST['email']
        phoneNumber = request.POST['phoneNumber']
        interviewName = request.POST['interviewName']
        data = innerCreateCandidate(
            candidateName, email, phoneNumber, interviewName)
        pageText = getCandidateManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')


# 响应前端“删除候选人”
@login_required
def delCandidate(request):
    if request.POST:
        id = request.POST['id']
        data = innerDeleteCandidate(id)
        pageText = getCandidateManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')


# 响应前端“编辑候选人”
@login_required
def editCandidate(request):
    if request.POST:
        candidateName = request.POST['candidateName']
        email = request.POST['email']
        phoneNumber = request.POST['phoneNumber']
        interviewName = request.POST['interviewName']
        id = request.POST['id']
        data = innerEditCandidate(
            candidateName,
            email,
            phoneNumber,
            interviewName,
            id)
        pageText = getCandidateManageRender()
        data['pageText'] = pageText
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@login_required
def batchImportCandidate(request):
    info = {}
    pageText = getCandidateManageRender()
    excelFile = request.FILES.get('excelfile')
    if excelFile is None:

        info['status'] = 'fail'
        info['pageText'] = pageText
        info['message'] = u'上传文件不能为空'
        return HttpResponse(json.dumps(info), content_type='application/json')
    elif len(re.findall(excelPattern, str(excelFile))) == 0:
        info['status'] = 'fail'
        info['pageText'] = pageText
        info['message'] = u'上传文件格式错误'
        return HttpResponse(json.dumps(info), content_type='application/json')
    excelfile = ExcelFile.objects.create(file=excelFile)
    fileurl = excelfile.file.url[1:]
    try:
        data = xlrd.open_workbook(excelfile.file.url[1:])
        sheet = data.sheet_by_index(0)
        rows = sheet.nrows
        for row in range(1, rows):
            name = sheet.cell(row, 0).value
            email = sheet.cell(row, 1).value
            phoneNumber = str(int(sheet.cell(row, 2).value))
            interviewName = sheet.cell(row, 3).value
            message = judgeCandidateInfo(
                name, email, phoneNumber, interviewName)
            if message != 'success':
                raise Error(ADD, CANDIDATE, (u'第%d行:' % row) + message)

        for row in range(1, rows):
            name = sheet.cell(row, 0).value
            email = sheet.cell(row, 1).value
            phoneNumber = str(int(sheet.cell(row, 2).value))
            interviewName = sheet.cell(row, 3).value
            intw = Interview.objects.get(name=interviewName)
            cand = Candidate.objects.create(
                name=name,
                email=email,
                phoneNumber=phoneNumber,
                interview=intw)
            cand.save()
        info['status'] = 'success'
    except Error as e:
        info['status'] = 'fail'
        info['message'] = e.errorInfo
    except Exception as e:
        info['status'] = 'fail'
    if os.path.exists(fileurl):
        os.remove(fileurl)

    pageText = getCandidateManageRender()
    info['pageText'] = pageText
    return HttpResponse(json.dumps(info), content_type='application/json')


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        company = request.POST['company']
        password = request.POST['password']
        passwordConfirm = request.POST['passwordConfirm']
        verificationNum = request.POST['verificationNum']
        verificationInput = request.POST['verificationInput']
        data = addHR(
            name,
            email,
            company,
            password,
            passwordConfirm,
            verificationNum,
            verificationInput)
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def login(request):
    import random
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == '' or password == '':
            message = u'输入不能为空'
            return render(
                request, 'login.html', {
                    'message': message, 'verificationNum': random.randint(
                        0, 9)})
        user = User.objects.filter(username=username, password=password)
        if user and user[0].is_active:
            auth.login(request, user[0])
            response = HttpResponseRedirect('/ink/HRManage/')
            return response
        else:
            message = u'用户名或密码错误'
            return render(
                request, 'login.html', {
                    'message': message, 'verificationNum': random.randint(
                        0, 9)})

    return render(
        request, 'login.html', {
            'verificationNum': random.randint(
                0, 9)})


@login_required
def logout(request):
    auth.logout(request)
    data = {'status': 'success'}
    return HttpResponse(json.dumps(data), content_type='application/json')
    # return HttpResponseRedirect('/ink/login/')


def addHR(
        name,
        email,
        company,
        password,
        passwordConfirm,
        verificationNum,
        verificationInput):
    try:
        if len(name) > NAME_MAX_LENGTH:
            raise Error(ADD, HRMANAGER, NAME_TOO_LONG)
        if len(name) == 0 or len(email) == 0 or len(company) == 0 \
                or len(password) == 0 or len(passwordConfirm) == 0:
            raise Error(ADD, HRMANAGER, NOT_EMPTY)
        _user = User.objects.filter(username=email)
        if _user:
            raise Error(ADD, HRMANAGER, u'该邮箱已注册')
        if password != passwordConfirm:
            raise Error(ADD, HRMANAGER, u'密码与确认密码不同')
        if verificationInput.lower() != verification[int(verificationNum)]:
            raise Error(ADD, HRMANAGER, u'验证码错误')
        emailMatchRes = re.match(emailForm, email)
        if emailMatchRes is None:
            raise Error(ADD, HRMANAGER, EMAIL_FORM_ERROR)
        if len(password) <= 8:
            raise Error(ADD, HRMANAGER, u'密码长度必须大于8')
        user = User.objects.create(username=email, password=password)
        hr = HR.objects.create(
            user=user,
            name=name,
            email=email,
            company=company)
        hr.save()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def innerCreateRoom(
        roomName,
        startTime,
        logo,
        interviewerName,
        interviewerEmail):
    try:
        if len(roomName) > NAME_MAX_LENGTH:
            raise Error(ADD, ROOM, NAME_TOO_LONG)
        # starttime, logo
        #sufix = os.path.splitext(str(logo))[1][1:]
        if len(interviewerName) > NAME_MAX_LENGTH:
            raise Error(ADD, ROOM, NAME_TOO_LONG)
        if len(roomName) == 0 or len(interviewerName) == 0 or len(
                startTime) == 0 or logo is None:
            raise Error(ADD, ROOM, NOT_EMPTY)

        timeMatchRes = re.match(timeForm, startTime)
        if timeMatchRes is None:
            raise Error(ADD, ROOM, TIME_FORM_ERROR)

        intws = Interview.objects.filter(name=roomName)
        if len(intws) != 0:
            raise Error(ADD, ROOM, SAME_NAME_ERROR)

        emailMatchRes = re.match(emailForm, interviewerEmail)
        if emailMatchRes is None:
            raise Error(ADD, ROOM, EMAIL_FORM_ERROR)
        if len(re.findall(imagePattern, str(logo))) == 0:
            raise Error(ADD, ROOM, FILE_FORM_ERROR)
        intw = Interview.objects.create(
            name=roomName, startTime=startTime, logo=logo)
        intw.save()
        intwer = Interviewer.objects.create(
            name=interviewerName,
            email=interviewerEmail,
            interview=intw)
        intwer.save()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def innerEditRoom(
        roomName,
        startTime,
        logo,
        interviewerName,
        interviewerEmail,
        id):
    try:
        if len(roomName) > NAME_MAX_LENGTH:
            raise Error(EDIT, ROOM, NAME_TOO_LONG)
        # starttime,logo

        if len(interviewerName) > NAME_MAX_LENGTH:
            raise Error(EDIT, ROOM, NAME_TOO_LONG)
        if len(roomName) == 0 or len(
                interviewerName) == 0 or len(startTime) == 0:
            raise Error(EDIT, ROOM, NOT_EMPTY)
        timeMatchRes = re.match(timeForm, startTime)
        if timeMatchRes is None:
            raise Error(EDIT, ROOM, TIME_FORM_ERROR)
        emailMatchRes = re.match(emailForm, interviewerEmail)
        if emailMatchRes is None:
            raise Error(EDIT, ROOM, EMAIL_FORM_ERROR)
        interviews = Interview.objects.filter(id=id)
        if len(interviews) != 1:
            raise Error(EDIT, ROOM, ROOM_NOT_EXIST)

        if roomName != interviews[0].name:
            tmptinerviews = Interview.objects.filter(name=roomName)
            if len(tmptinerviews) > 0:
                raise Error(EDIT, ROOM, SAME_NAME_ERROR)

        interviews[0].name = roomName
        interviews[0].startTime = startTime
        if logo is not None:
            if len(re.findall(imagePattern, str(logo))) == 0:
                raise Error(EDIT, ROOM, FILE_FORM_ERROR)
            originLogoUrl = interviews[0].logo.url[1:]
            interviews[0].logo = logo
            if os.path.exists(originLogoUrl):
                os.remove(originLogoUrl)
        interviews[0].save()

        interviewers = Interviewer.objects.filter(interview=interviews[0])
        if len(interviewers) != 1:
            raise Error(EDIT, ROOM, '')
        interviewers[0].name = interviewerName
        interviewers[0].email = interviewerEmail
        interviewers[0].save()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def innerDeleteRoom(theId):
    try:
        # id = int(theId)
        id = theId
        interview = Interview.objects.filter(id=id)
        if len(interview) != 1:
            raise Error(DELETE, ROOM, ROOM_NOT_EXIST)
        interviewer = Interviewer.objects.filter(interview=interview[0])
        if len(interviewer) != 1:
            raise Error(DELETE, ROOM, ROOM_NOT_EXIST)
        interview[0].delete()
        interviewer[0].delete()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def judgeCandidateInfo(name, email, phoneNumber, interviewName):
    length = len(name)
    if length == 0 or len(email) == 0 or len(phoneNumber) == 0 or len(interviewName) == 0:
        return NOT_EMPTY
    if length > NAME_MAX_LENGTH:
        return NAME_TOO_LONG

    emailMatchRes = re.match(emailForm, email)
    if emailMatchRes is None:
        return EMAIL_FORM_ERROR

    phoneMatchRes = re.match(phoneNumberForm, phoneNumber)
    if phoneMatchRes is None:
        return PHONENUMBER_FORM_ERROR

    intwList = Interview.objects.filter(name=interviewName)
    if len(intwList) != 1:
        return ROOM_NOT_EXIST
    return 'success'


def innerCreateCandidate(name, email, phoneNumber, interviewName):
    try:
        message = judgeCandidateInfo(name, email, phoneNumber, interviewName)
        if message == 'success':
            intw = Interview.objects.get(name=interviewName)
            cand = Candidate.objects.create(
                name=name,
                email=email,
                phoneNumber=phoneNumber,
                interview=intw)
            cand.save()
            return {'status': 'success'}
        else:
            raise Error(ADD, CANDIDATE, message)
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def innerEditCandidate(name, email, phoneNumber, interviewName, id):
    try:
        length = len(name)
        if length == 0 or len(email) == 0 or len(phoneNumber) == 0 or len(interviewName) == 0:
            raise Error(EDIT, CANDIDATE, NOT_EMPTY)
        if length > NAME_MAX_LENGTH:
            raise Error(EDIT, CANDIDATE, NAME_TOO_LONG)

        emailMatchRes = re.match(emailForm, email)
        if emailMatchRes is None:
            raise Error(EDIT, CANDIDATE, EMAIL_FORM_ERROR)

        phoneMatchRes = re.match(phoneNumberForm, phoneNumber)
        if phoneMatchRes is None:
            raise Error(EDIT, CANDIDATE, PHONENUMBER_FORM_ERROR)

        intwList = Interview.objects.filter(name=interviewName)
        if len(intwList) != 1:
            raise Error(EDIT, CANDIDATE, ROOM_NOT_EXIST)

        id = int(id)
        candidate = Candidate.objects.filter(id=id)
        if len(candidate) != 1:
            raise Error(EDIT, CANDIDATE, CANDIDATE_NOT_EXIST)

        candidate[0].name = name
        candidate[0].email = email
        candidate[0].phoneNumber = phoneNumber
        candidate[0].interview = intwList[0]
        candidate[0].save()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def innerDeleteCandidate(theId):
    try:
        id = int(theId)
        candidate = Candidate.objects.filter(id=id)
        if len(candidate) != 1:
            raise Error(DELETE, CANDIDATE, CANDIDATE_NOT_EXIST)
        candidate[0].delete()
        return {'status': 'success'}
    except Error as e:
        return {'status': 'fail', 'message': e.errorInfo}


def downloadExampleExcel(request):
    filename = "example.xlsx"
    filepath = BASE_DIR + '/static/media/' + filename
    data = open(filepath, "rb").read()
    # data = readFile(filepath)
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
    return response


# 生成根据面试官邮箱编码后的roomId
def getEncodedRoomID(roomId):  # roomId是整数，retId是一个字符串
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
