# coding=utf-8

from django.test import *
from django.test.client import Client
from views import *

LONG_STR_31 = '1234567890123456789012345678901'


class TestTestCase(TestCase):

    def setUp(self):
        intw1 = Interview.objects.create(
            name='jisuanke',
            startTime="2016-11-30 15:30",
            logo="logo/1.jpg")
        Interviewer.objects.create(
            name="wyx",
            email='940994060@qq.com',
            interview=intw1)
        intw2 = Interview.objects.create(
            name="crazyzoopia",
            startTime="2016-11-30 16:30",
            logo="logo/2.jpg")
        Interviewer.objects.create(
            name="qwe",
            email='940994060@qq.com',
            interview=intw2)
        Candidate.objects.create(
            name='gg',
            email='940994060@qq.com',
            phoneNumber='13123456789',
            interview=intw1,
            state=NOT_START)
        User.objects.create(username='1@qq.com', password='123456789')



    def test_inner_create_room(self):
        name1 = ''
        name2 = 'software project'
        name3 = LONG_STR_31
        time1 = "2016-12-30 03:37"
        time2 = "2016-13-30 03:37"
        logo1 = 'logo/1.jpg'
        interviewerName1 = 'cyd'
        interviewerName2 = ''
        interviewerEmail1 = '940994060@qq.com'
        interviewerEmail2 = '1@1'
        self.assertEqual(
            innerCreateRoom(
                name1, time1, logo1, interviewerName1, interviewerEmail1), {
                'status': 'fail', 'message': u'输入不能为空'})

        self.assertEqual(
            innerCreateRoom(
                name3, time1, logo1, interviewerName1, interviewerEmail1), {
                'status': 'fail', 'message': u'内容过长'})

        self.assertEqual(
            innerCreateRoom(
                name2, time1, logo1, interviewerName1, interviewerEmail2), {
                'status': 'fail', 'message': u'邮箱格式错误'})

        self.assertEqual(
            innerCreateRoom(
                name2, time2, logo1, interviewerName1, interviewerEmail1), {
                'status': 'fail', 'message': u'时间格式错误'})

        self.assertEqual(
            innerCreateRoom(
                name2, time1, logo1, interviewerName1, interviewerEmail1), {
                'status': 'success'})

        self.assertEqual(
            innerCreateRoom(
                name2, time1, logo1, interviewerName1, interviewerEmail1), {
                'status': 'fail', 'message': u'房间名称不能重复'})

    def test_inner_edit_room(self):
        name1 = ''
        name2 = 'software'
        name3 = LONG_STR_31
        time1 = "2016-12-30 03:37"
        time2 = "2016-13-30 03:37"
        logo1 = 'logo/1.jpg'
        interviewerName1 = 'cyd'
        interviewerEmail1 = '940994060@qq.com'
        interviewerEmail2 = '1@1'
        theId = Interview.objects.all()[0].id
        self.assertEqual(
            innerEditRoom(
                name1, time1, logo1, interviewerName1, interviewerEmail1, theId), {
                'status': 'fail', 'message': u'输入不能为空'})

        self.assertEqual(
            innerEditRoom(
                name3, time1, logo1, interviewerName1, interviewerEmail1, theId), {
                'status': 'fail', 'message': u'内容过长'})

        self.assertEqual(
            innerEditRoom(
                name2, time1, logo1, interviewerName1, interviewerEmail2, theId), {
                'status': 'fail', 'message': u'邮箱格式错误'})

        self.assertEqual(
            innerEditRoom(
                name2, time2, logo1, interviewerName1, interviewerEmail1, theId), {
                'status': 'fail', 'message': u'时间格式错误'})

        self.assertEqual(innerEditRoom(name2, time1, logo1, interviewerName1,
                                       interviewerEmail1, -1), {'status': 'fail', 'message': u'房间不存在'})

        self.assertEqual(
            innerEditRoom(
                name2, time1, logo1, interviewerName1, interviewerEmail1, theId), {
                'status': 'success'})

        self.assertEqual(
            innerEditRoom(
                'crazyzoopia', time1, logo1, interviewerName1, interviewerEmail1, theId), {
                'status': 'fail', 'message': u'房间名称不能重复'})

    def test_inner_delete_room(self):
        theId = Interview.objects.all()[0].id
        self.assertEqual(innerDeleteRoom(-1),
                         {'status': 'fail', 'message': u'房间不存在'})
        self.assertEqual(innerDeleteRoom(theId), {'status': 'success'})

    def test_judge_candidate_info(self):
        name1 = ''
        name2 = 'cgb'
        name3 = LONG_STR_31
        candidateEmail1 = '940994060@qq.com'
        candidateEmail2 = '1@1'
        phoneNumber1 = '123'
        phoneNumber2 = '13123456789'
        interviewerName1 = 'jisuanke'
        interviewerName2 = 'notexist'
        self.assertEqual(
            judgeCandidateInfo(
                name1,
                candidateEmail1,
                phoneNumber2,
                interviewerName1),
            u'输入不能为空')
        self.assertEqual(
            judgeCandidateInfo(
                name3,
                candidateEmail1,
                phoneNumber2,
                interviewerName1),
            u'内容过长')
        self.assertEqual(
            judgeCandidateInfo(
                name2,
                candidateEmail2,
                phoneNumber2,
                interviewerName1),
            u'邮箱格式错误')
        self.assertEqual(
            judgeCandidateInfo(
                name2,
                candidateEmail1,
                phoneNumber1,
                interviewerName1),
            u'手机号码格式错误')
        self.assertEqual(
            judgeCandidateInfo(
                name2,
                candidateEmail1,
                phoneNumber2,
                interviewerName2),
            u'房间不存在')
        self.assertEqual(
            judgeCandidateInfo(
                name2,
                candidateEmail1,
                phoneNumber2,
                interviewerName1),
            'success')

    def test_inner_create_candidate(self):
        name1 = ''
        name2 = 'cgb'
        name3 = LONG_STR_31
        candidateEmail1 = '940994060@qq.com'
        candidateEmail2 = '1@1'
        phoneNumber1 = '123'
        phoneNumber2 = '13123456789'
        interviewerName1 = 'jisuanke'
        interviewerName2 = 'notexist'
        self.assertEqual(
            innerCreateCandidate(
                name1, candidateEmail1, phoneNumber2, interviewerName1), {
                'status': 'fail', 'message': u'输入不能为空'})
        self.assertEqual(
            innerCreateCandidate(
                name3, candidateEmail1, phoneNumber2, interviewerName1), {
                'status': 'fail', 'message': u'内容过长'})
        self.assertEqual(
            innerCreateCandidate(
                name2, candidateEmail2, phoneNumber2, interviewerName1), {
                'status': 'fail', 'message': u'邮箱格式错误'})
        self.assertEqual(
            innerCreateCandidate(
                name2, candidateEmail1, phoneNumber1, interviewerName1), {
                'status': 'fail', 'message': u'手机号码格式错误'})
        self.assertEqual(
            innerCreateCandidate(
                name2, candidateEmail1, phoneNumber2, interviewerName2), {
                'status': 'fail', 'message': u'房间不存在'})
        self.assertEqual(
            innerCreateCandidate(
                name2, candidateEmail1, phoneNumber2, interviewerName1), {
                'status': 'success'})

    def test_inner_edit_candidate(self):
        name1 = ''
        name2 = 'cgb'
        name3 = LONG_STR_31
        candidateEmail1 = '940994060@qq.com'
        candidateEmail2 = '1@1'
        phoneNumber1 = '123'
        phoneNumber2 = '13123456789'
        interviewerName1 = 'jisuanke'
        interviewerName2 = 'notexist'
        theId = Candidate.objects.all()[0].id
        self.assertEqual(
            innerEditCandidate(
                name1, candidateEmail1, phoneNumber2, interviewerName1, theId), {
                'status': 'fail', 'message': u'输入不能为空'})
        self.assertEqual(
            innerEditCandidate(
                name3, candidateEmail1, phoneNumber2, interviewerName1, theId), {
                'status': 'fail', 'message': u'内容过长'})
        self.assertEqual(
            innerEditCandidate(
                name2, candidateEmail2, phoneNumber2, interviewerName1, theId), {
                'status': 'fail', 'message': u'邮箱格式错误'})
        self.assertEqual(
            innerEditCandidate(
                name2, candidateEmail1, phoneNumber1, interviewerName1, theId), {
                'status': 'fail', 'message': u'手机号码格式错误'})
        self.assertEqual(
            innerEditCandidate(
                name2, candidateEmail1, phoneNumber2, interviewerName2, theId), {
                'status': 'fail', 'message': u'房间不存在'})
        self.assertEqual(innerEditCandidate(name2, candidateEmail1, phoneNumber2,
                                            interviewerName1, -1), {'status': 'fail', 'message': u'候选人不存在'})
        self.assertEqual(
            innerEditCandidate(
                name2, candidateEmail1, phoneNumber2, interviewerName1, theId), {
                'status': 'success'})

    def test_inner_delete_candidate(self):
        theId = Candidate.objects.all()[0].id
        self.assertEqual(innerDeleteCandidate(-1),
                         {'status': 'fail', 'message': u'候选人不存在'})
        self.assertEqual(innerDeleteCandidate(theId),
                         {'status': 'success'})

    def test_add_HR(self):
        name1 = ''
        name2 = 'cgb'
        name3 = LONG_STR_31
        email1 = '1@qq.com'
        email2 = '1234'
        email3 = '12345@qq.com'
        company = 'tsinghua university'
        password1 = '1'
        password2 = '123456789'
        passwordConfirm1 = '1'
        passwordConfirm2 = '123456789'
        verificationNum = 0
        verificationInput1 = 'abcde'
        verificationInput2 = 'l6fwi'
        self.assertEqual(addHR(name1,
                               email3,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'输入不能为空'})
        self.assertEqual(addHR(name3,
                               email3,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'内容过长'})
        self.assertEqual(addHR(name2,
                               email1,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'该邮箱已注册'})
        self.assertEqual(addHR(name2,
                               email2,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'邮箱格式错误'})
        self.assertEqual(addHR(name2,
                               email3,
                               company,
                               password1,
                               passwordConfirm1,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'密码长度必须大于8'})
        self.assertEqual(addHR(name2,
                               email3,
                               company,
                               password2,
                               passwordConfirm1,
                               verificationNum,
                               verificationInput2),
                         {'status': 'fail',
                          'message': u'密码与确认密码不同'})
        self.assertEqual(addHR(name2,
                               email3,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput1),
                         {'status': 'fail',
                          'message': u'验证码错误'})
        self.assertEqual(addHR(name2,
                               email3,
                               company,
                               password2,
                               passwordConfirm2,
                               verificationNum,
                               verificationInput2),
                         {'status': 'success'})

    def test_getRoomlist(self):
        roomList = getRoomList()
        self.assertEqual(roomList[0]['roomname'], 'jisuanke')
        self.assertEqual(roomList[1]['roomname'], 'crazyzoopia')

    def test_getCandidateListOfRoom(self):
        theId = Interview.objects.all()[0].id
        candList = getCandidateListOfRoom(theId)
        self.assertEqual(candList[0]['candidateName'], 'gg')

    def test_getAllCandidate(self):
        candidateList = getAllCandidate()
        self.assertEqual(candidateList[0]['name'], 'jisuanke')
        self.assertEqual(candidateList[0]['candList'][
                         0].get('candidateName'), 'gg')

    def test_BKDR_hash(self):
        email1 = "yd-chen14@mails.tsinghua.edu.cn"
        email2 = "529641713@qq.com"
        self.assertEqual(BKDRHash(email1), 480801869)
        self.assertEqual(BKDRHash(email2), 1718126729)

    def test_get_encoded_roomId(self):
        rooms = Interview.objects.all()
        roomId = rooms[0].id
        self.assertEqual(getEncodedRoomID(roomId), "283202752_" + str(roomId))


    # Add in Dec. 2nd
    def test_get_HR_manage_render(self):
        HRManageRender = getHRManageRender()
        self.assertEqual((u"HR管理房间" in HRManageRender), True)

    def test_get_room_manage_render(self):
        roomManageRender = getRoomManageRender()
        self.assertEqual((u"房间信息" in roomManageRender), True)

    def test_get_candidate_manage_render(self):
        candidateManageRender = getCandidateManageRender()
        self.assertEqual((u"候选人" in candidateManageRender), True)

    def test_login(self):
        response1 = self.client.post("/ink/login/", {'username': '', 'password': '123456789'})
        response2 = self.client.post("/ink/login/", {'username': '1@qq.com', 'password': '12345'})
        response3 = self.client.post("/ink/login/", {'username': '1@qq.com', 'password': '123456789'})

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 302)

    def test_register(self):
        response1 = self.client.post("/ink/register/",
                                     {'name': 'victor', 'email': '123456789@qq.com',
                                      'company': 'jisuanke', 'password': 'abcdefg',
                                      'passwordConfirm': 'abcdefg', 'verificationNum': '6',
                                      'verificationInput': '6'})
        self.assertEqual(response1.status_code, 200)

    def test_download_example_excel(self):
        response1 = self.client.post("/ink/downloadExampleExcel/", {'username': '', 'password': '123456789'})
        self.assertEqual(response1.status_code, 200)







     # response1 = self.client.post('/ink/getCandidate/?room=' + getEncodedRoomID(roomId))
     #    self.assertEqual(response1.status_code, 200)

    # def test_add_activity_group_user_name_error(self):
    #     client = Client()
    #     dic = {
    #         'activity_group_name': 'software engineering',
    #         'admin_user': [
    #             'lizeyan',
    #             '1231'
    #         ],
    #         'normal_user': [
    #             'sunweijun',
    #             '122222'
    #         ]
    #     }
    #     self.assertTrue(client.login(
    #         username='lvxin',
    #         password='123456'
    #     ))
    #     answer = client.post(
    #         '/activity_group/',
    #         json.dumps(dic),
    #         content_type='application/json',
    #     )
    #     answer_json = json.loads(answer.content.decode())
    #     self.assertEqual(answer.status_code, 201)
    #     self.assertEqual(answer_json['status'], 'CREATE_SUCCESS_SOME_ADD_FAILED')
    #     self.assertEqual(answer_json['suggestion'], '创建成功，但是某些成员添加失败')