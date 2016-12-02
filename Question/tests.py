# coding=utf-8

from django.test import TestCase, Client
from models import *
from views import *
from django.shortcuts import get_object_or_404


class ChoiceTestCase(TestCase):
    def setUp(self):
        interview = Interview.objects.create(
            name="unittest",
            startTime="2016-07-10 21:59",
            logo="logo.jpg"
        )
        Interviewer.objects.create(
            name="victor",
            email="yd-chen14@mails.tsinghua.edu.cn",
            interview=interview
        )
        Choice.objects.create(
            title="sodagreen",
            stem="sodared",
            optionA="sodaA",
            optionB="sodaB",
            optionNum=2,
            answer="AB",
            interview=interview
        )
        Choice.objects.create(
            title="99",
            stem="rougai!!",
            optionA="luren1",
            optionB="luren2",
            optionC="luren3",
            optionD="luren4",
            optionNum=4,
            answer="ABD",
            interview=interview
        )
        Choice.objects.create(
            title="summer",
            stem="which ones are in the summer album?",
            optionA="PeterAndWolf",
            optionB="Everyone",
            optionC="Violently Beautiful",
            optionD="He summers the summer",
            optionE="Go home earlier",
            optionF="Dance Together",
            optionNum=6,
            answer="ADF",
            interview=interview
        )

    # 【addChoice()】
    def test_add_choice(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        response1 = self.client.post('/ink/addChoice/?room=' + getEncodedRoomID(roomId),
                                     {'choiceTitle': "hahaha",
                                      'choiceStem': "who is laughing?",
                                      'A': "xdy",
                                      'B': "lyx",
                                      'C': "cyd",
                                      'D': "xcy",
                                      'E': "",
                                      'F': "",
                                      'optionNum': "4",
                                      'choiceAnswer': "ABCD"})
        self.assertEqual(response1.status_code, 200)
        try:
            choice1 = Choice.objects.get(title="hahaha")
        except Choice.DoesNotExist:
            choice1 = None
        if choice1 is not None:
            self.assertEqual(choice1.stem, "who is laughing?")
            self.assertEqual(choice1.answer, "ABCD")
            self.assertEqual(choice1.optionNum, 4)
            self.assertEqual(choice1.optionA, "xdy")

        # 异常：错误url
        response2 = self.client.post('/addchoice/?room=' + getEncodedRoomID(roomId),
                                     {'choiceTitle': "hahaha",
                                      'choiceStem': "who is laughing?",
                                      'A': "xdy",
                                      'B': "lyx",
                                      'C': "cyd",
                                      'D': "xcy",
                                      'E': "",
                                      'F': "",
                                      'optionNum': "4",
                                      'choiceAnswer': "ABCD"})
        self.assertEqual(response2.status_code, 404)

        # 异常：错误request key
        with self.assertRaises(KeyError):
            self.client.post('/ink/addCode/?room=' + getEncodedRoomID(roomId),
                             {'choiceTitle': "hahaha",
                              'choiceStem': "who is laughing?",
                              'A': "xdy",
                              'B': "lyx",
                              'C': "cyd",
                              'D': "xcy",
                              'optionNum': "4",
                              'choiceAnswer': "ABCD"})


    # 【innerAddChoice()】
    def test_inner_add_choice(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        successAddChoiceInfo = innerAddChoice(
            "ha", "who is laughing?", "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", roomId)
        self.assertEqual(successAddChoiceInfo['status'], 'success')
        self.assertEqual(successAddChoiceInfo['message'], u"添加选择题成功！")

        # 异常：房间id不存在
        noRoomIdInfo = innerAddChoice(
            'no room id', 'nothing', "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerAddChoice(
            '99', 'nothing', "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerAddChoice(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "xdy", "lyx", "cyd", "xcy", "", "", "4", "BD", roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerAddChoice(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD",
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：没有勾选答案
        noOptionsCheckedInfo = innerAddChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "cyd", "xcy", "", "", "4", "", roomId)
        self.assertEqual(noOptionsCheckedInfo['status'], 'fail')
        self.assertEqual(noOptionsCheckedInfo['message'], NO_OPTIONS_CHECKED)

        # 异常：空输入
        emptyInputInfo = innerAddChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "", "xcy", "", "", "4", "ABCD", roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)

        # 异常：答案非法
        illegalAnswerInfo = innerAddChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "cyd", "xcy", "", "", "4", "AE", roomId)
        self.assertEqual(illegalAnswerInfo['status'], 'fail')
        self.assertEqual(illegalAnswerInfo['message'], ILLEGAL_ANSWER)

        # 异常：存在相同选项
        reduplicativeOptionsInfo = innerAddChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "xcy", "xcy", "", "", "4", "CD", roomId)
        self.assertEqual(reduplicativeOptionsInfo['status'], 'fail')
        self.assertEqual(reduplicativeOptionsInfo['message'], REDUPLICATIVE_OPTIONS)

    # 【delChoice(), innerDel()】
    def test_del_choice(self):
        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        choices = Choice.objects.all()

        # 【delChoice()】
        # 正常删除
        response1 = self.client.post(
            '/ink/delChoice/?room=' + getEncodedRoomID(roomId), {'id': "choice_" + str(choices[1].id)})
        self.assertEqual(response1.status_code, 200)

        # 异常：错误url
        response2 = self.client.post('/delChoice/?room=' + getEncodedRoomID(roomId), {'id': "choice_" + str(choices[0].id)})
        self.assertEqual(response2.status_code, 404)

        # 【innerDel( type=choice )】
        # 正常删除
        successDelInfo = innerDel(
            'choice', "choice_" + str(choices[0].id), roomId)
        self.assertEqual(successDelInfo['status'], "success")
        self.assertEqual(successDelInfo['message'], u"删除选择题成功！")

        ninetynine = Choice.objects.filter(title='99')
        self.assertEqual(len(ninetynine), 0)

        # 异常：房间id不存在
        noRoomInfo = innerDel('Choice', "choice_" + str(choices[0].id), roomId+1)
        self.assertEqual(noRoomInfo['status'], "fail")
        self.assertEqual(noRoomInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：要删除的简答题id不存在
        noChoiceId = innerDel('Choice', "choice_" + str(choices[0].id+10), roomId)
        self.assertEqual(noChoiceId['status'], "fail")
        self.assertEqual(noChoiceId['message'], NO_SUCH_ID)

    # 【editChoice()】
    def test_edit_choice(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        choices = Choice.objects.all()

        # 正常添加
        response1 = self.client.post('/ink/editChoice/?room=' + getEncodedRoomID(roomId),
                                     {'choiceTitle': "hahaha",
                                      'choiceStem': "who is laughing?",
                                      'A': "xdy",
                                      'B': "lyx",
                                      'C': "cyd",
                                      'D': "xcy",
                                      'E': "",
                                      'F': "",
                                      'optionNum': "4",
                                      'choiceAnswer': "ABCD",
                                      'choiceId': "choice_"+str(choices[0].id)})
        self.assertEqual(response1.status_code, 200)
        try:
            choice1 = Choice.objects.get(title="hahaha")
        except Choice.DoesNotExist:
            choice1 = None
        if choice1 is not None:
            self.assertEqual(choice1.stem, "who is laughing?")
            self.assertEqual(choice1.answer, "ABCD")
            self.assertEqual(choice1.optionNum, 4)
            self.assertEqual(choice1.optionA, "xdy")
            self.assertEqual(choice1.id, choices[0].id)

        # 异常：错误url
        response2 = self.client.post('/editchoice/?room=' + getEncodedRoomID(roomId),
                                     {'choiceTitle': "hahaha",
                                      'choiceStem': "who is laughing?",
                                      'A': "xdy",
                                      'B': "lyx",
                                      'C': "cyd",
                                      'D': "xcy",
                                      'E': "",
                                      'F': "",
                                      'optionNum': "4",
                                      'choiceAnswer': "ABCD",
                                      'choiceId': "choice_"+str(choices[0].id)})
        self.assertEqual(response2.status_code, 404)

        # 异常：错误request key
        with self.assertRaises(KeyError):
            self.client.post('/ink/editCode/?room=' + getEncodedRoomID(roomId),
                             {'choiceTitle': "hahaha",
                              'choiceStem': "who is laughing?",
                              'A': "xdy",
                              'B': "lyx",
                              'C': "cyd",
                              'D': "xcy",
                              'optionNum': "4",
                              'choiceAnswer': "ABCD",
                              'choiceId': "choice_"+str(choices[0].id)})

    # 【innerEditChoice()】
    def test_inner_edit_choice(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        choices = Choice.objects.all()
        editId = "choice_"+str(choices[0].id)

        # 正常编辑
        successEditChoiceInfo = innerEditChoice(
            "ha", "who is laughing?", "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", editId, roomId)
        self.assertEqual(successEditChoiceInfo['status'], 'success')
        self.assertEqual(successEditChoiceInfo['message'], u"编辑选择题成功！")

        # 异常：房间id不存在
        noRoomIdInfo = innerEditChoice(
            'no room id', 'nothing', "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", editId, roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerEditChoice(
            '99', 'nothing', "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD", editId, roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerEditChoice(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "xdy", "lyx", "cyd", "xcy", "", "", "4", "BD", editId, roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerEditChoice(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "xdy", "lyx", "cyd", "xcy", "", "", "4", "ABCD",
            editId, roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：没有勾选答案
        noOptionsCheckedInfo = innerEditChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "cyd", "xcy", "", "", "4", "", editId, roomId)
        self.assertEqual(noOptionsCheckedInfo['status'], 'fail')
        self.assertEqual(noOptionsCheckedInfo['message'], NO_OPTIONS_CHECKED)

        # 异常：空输入
        emptyInputInfo = innerEditChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "", "xcy", "", "", "4", "ABCD", editId, roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)

        # 异常：答案非法
        illegalAnswerInfo = innerEditChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "cyd", "xcy", "", "", "4", "AE", editId, roomId)
        self.assertEqual(illegalAnswerInfo['status'], 'fail')
        self.assertEqual(illegalAnswerInfo['message'], ILLEGAL_ANSWER)

        # 异常：存在相同选项
        reduplicativeOptionsInfo = innerEditChoice(
            'hallo', 'who is laughing?', "xdy", "lyx", "xcy", "xcy", "", "", "4", "CD", editId, roomId)
        self.assertEqual(reduplicativeOptionsInfo['status'], 'fail')
        self.assertEqual(reduplicativeOptionsInfo['message'], REDUPLICATIVE_OPTIONS)


class CompletionTestCase(TestCase):

    def setUp(self):
        interview = Interview.objects.create(
            name="unittest",
            startTime="2016-07-10 21:59",
            logo="logo.jpg"
        )
        Interviewer.objects.create(
            name="victor",
            email="yd-chen14@mails.tsinghua.edu.cn",
            interview=interview
        )
        Completion.objects.create(
            title="weird cat",
            stem="mio~mia~[]~",
            answer="ligoudan",
            interview=interview)
        Completion.objects.create(
            title="cold star",
            stem="there're [] stars in the sky.",
            answer="beautiful",
            interview=interview)
        Completion.objects.create(
            title="black T-shirt",
            stem="black T-shirt is cool or warm? []",
            answer="both",
            interview=interview)

    # 【addCompletion()】
    def test_add_completion(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        response1 = self.client.post('/ink/addCompletion/?room=' + getEncodedRoomID(roomId),
                                     {'completionTitle': "hahaha",
                                      'completionStem': "who is laughing? []",
                                      'completionAnswer': "genius"})
        self.assertEqual(response1.status_code, 200)
        try:
            completion1 = Completion.objects.get(title="hahaha")
        except Completion.DoesNotExist:
            completion1 = None
        if completion1 is not None:
            self.assertEqual(completion1.stem, "who is laughing? []")
            self.assertEqual(completion1.answer, "genius")

        # 异常：错误url
        response2 = self.client.post('/addCompletion/?room=' + getEncodedRoomID(roomId),
                                     {'completionTitle': "haha",
                                      'completionStem': "who is laughing? []",
                                      'completionAnswer': "genius"})
        self.assertEqual(response2.status_code, 404)

    # 【innerAddCompletion()】
    def test_inner_add_completion(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        successAddCompletionInfo = innerAddCompletion(
            "ha", "who is laughing? []", "genius", roomId)
        self.assertEqual(successAddCompletionInfo['status'], 'success')
        self.assertEqual(successAddCompletionInfo['message'], u"添加填空题成功！")

        # 异常：房间id不存在
        noRoomIdInfo = innerAddCompletion(
            'no room id', '[]', 'answer', roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerAddCompletion(
            'cold star', '[]', 'collllllld!', roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：没有空格标记
        noBlanksInfo = innerAddCompletion(
            "noblanks", "who is laughing?", "fool", roomId)
        self.assertEqual(noBlanksInfo['status'], 'fail')
        self.assertEqual(noBlanksInfo['message'], NO_BLANKS)

        # 异常：标题溢出
        titleOverFlowInfo = innerAddCompletion(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?[]",
            "sodagreen", roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerAddCompletion(
            "stembomb",
            "[]As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "awesome",
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：填空题答案溢出
        answerOverFlowInfo = innerAddCompletion(
            "answerbomb",
            "[]",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa",
            roomId)
        self.assertEqual(
            answerOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            answerOverFlowInfo['message'],
            COMPLETION_ANSWER_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerAddCompletion(
            '', 'who is laughing?[]', 'genius', roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)

    # 【delCompletion(); innerDel()】
    def test_del_completion(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        completions = Completion.objects.all()

        # 【delCompletion()】
        # 正常删除
        response1 = self.client.post(
            '/ink/delCompletion/?room=' + getEncodedRoomID(roomId), {'id': "completion_" + str(completions[1].id)})
        self.assertEqual(response1.status_code, 200)

        # 异常：错误url
        response2 = self.client.post('/delCompletion/?room=' + getEncodedRoomID(roomId), {'id': "completion_" + str(completions[1].id)})
        self.assertEqual(response2.status_code, 404)

        # 【innerDel( type=completion )】
        # 正常删除
        successDelInfo = innerDel(
            'completion', "completion_" + str(completions[1].id), roomId)
        self.assertEqual(successDelInfo['status'], "success")
        self.assertEqual(successDelInfo['message'], u"删除填空题成功！")

        coldStar = Completion.objects.filter(title='cold star')
        self.assertEqual(len(coldStar), 0)

        # 异常：房间id不存在
        noRoomInfo = innerDel('completion', "completion_" + str(completions[0].id), roomId+1)
        self.assertEqual(noRoomInfo['status'], "fail")
        self.assertEqual(noRoomInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：要删除的填空题id不存在
        noCompletionId = innerDel('completion', "completion_" + str(completions[0].id+10), roomId)
        self.assertEqual(noCompletionId['status'], "fail")
        self.assertEqual(noCompletionId['message'], NO_SUCH_ID)

    # 【editCompletion()】
    def test_edit_completion(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        completions = Completion.objects.all()

        # 正常编辑
        response1 = self.client.post('/ink/editCompletion/?room=' + getEncodedRoomID(roomId),
                                     {'completionTitle': "hahaha",
                                      'completionStem': "who is laughing? []",
                                      'completionAnswer': "genius",
                                      'completionId': "completion_"+str(completions[0].id)})
        self.assertEqual(response1.status_code, 200)
        try:
            completion1 = Completion.objects.get(title="hahaha")
        except Completion.DoesNotExist:
            completion1 = None
        if completion1 is not None:
            self.assertEqual(completion1.stem, "who is laughing? []")
            self.assertEqual(completion1.answer, "genius")

    # 【innerEditCompletion()】
    def test_inner_edit_completion(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        completions = Completion.objects.all()
        editId = "completion_"+str(completions[0].id)

        # 正常编辑
        successEditCompletionInfo = innerEditCompletion(
            "ha", "who is laughing? []", "genius", editId, roomId)
        self.assertEqual(successEditCompletionInfo['status'], 'success')
        self.assertEqual(successEditCompletionInfo['message'], u"编辑填空题成功！")
        self.assertEqual(completions[0].title, "ha")

        # 异常：房间id不存在
        noRoomIdInfo = innerEditCompletion(
            'no room id', '[]', 'answer', editId, roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerEditCompletion(
            'cold star', '[]', 'collllllld!', editId, roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：没有空格标记
        noBlanksInfo = innerEditCompletion(
            "noblanks", "who is laughing?", "fool", editId, roomId)
        self.assertEqual(noBlanksInfo['status'], 'fail')
        self.assertEqual(noBlanksInfo['message'], NO_BLANKS)

        # 异常：标题溢出
        titleOverFlowInfo = innerEditCompletion(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?[]",
            "sodagreen", editId, roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerEditCompletion(
            "stembomb",
            "[]As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "awesome",
            editId,
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：填空题答案溢出
        answerOverFlowInfo = innerEditCompletion(
            "answerbomb",
            "[]",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa",
            editId,
            roomId)
        self.assertEqual(
            answerOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            answerOverFlowInfo['message'],
            COMPLETION_ANSWER_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerEditCompletion(
            '', 'who is laughing?[]', 'genius', editId, roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)


class EssayTestCase(TestCase):
    def setUp(self):
        interview = Interview.objects.create(
            name="unittest",
            startTime="2016-07-10 21:59",
            logo="logo.jpg"
        )
        Interviewer.objects.create(
            name="victor",
            email="yd-chen14@mails.tsinghua.edu.cn",
            interview=interview
        )
        Essay.objects.create(
            title="sodagreen",
            stem="sodared",
            answer="sodablue",
            interview=interview
        )
        Essay.objects.create(
            title="iloveyou",
            stem="imustkeepsinging",
            answer="sleeping",
            interview=interview
        )
        Essay.objects.create(
            title="everyone",
            stem="idoesntmatterifyoufeellikenothing",
            answer="playingmusic",
            interview=interview
        )

    # 【addEssay()】
    def test_add_essay(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        response1 = self.client.post('/ink/addEssay/?room=' + getEncodedRoomID(roomId),
                                     {'essayTitle': "hahaha",
                                      'essayStem': "who is laughing?",
                                      'essayAnswer': "genius"})
        self.assertEqual(response1.status_code, 200)
        try:
            essay1 = Essay.objects.get(title="hahaha")
        except Essay.DoesNotExist:
            essay1 = None
        if essay1 is not None:
            self.assertEqual(essay1.stem, "who is laughing?")
            self.assertEqual(essay1.answer, "genius")

        # 异常：错误url
        response2 = self.client.post('/addEssay/?room=' + getEncodedRoomID(roomId),
                                     {'essayTitle': "haha",
                                      'essayStem': "who is laughing?",
                                      'essayAnswer': "genius"})
        self.assertEqual(response2.status_code, 404)

    # 【innerAddEssay()】
    def test_inner_add_essay(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        successAddEssayInfo = innerAddEssay(
            "ha", "who is laughing?", "genius", roomId)
        self.assertEqual(successAddEssayInfo['status'], 'success')
        self.assertEqual(successAddEssayInfo['message'], u"添加简答题成功！")

        # 异常：房间id不存在
        noRoomIdInfo = innerAddEssay(
            'no room id', 'nothing', 'answer', roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerAddEssay(
            'iloveyou', 'nothing', 'collllllld!', roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerAddEssay(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "sodagreen", roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerAddEssay(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "awesome",
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：简答题答案溢出
        answerOverFlowInfo = innerAddEssay(
            "answerbomb",
            "[]",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyasdfgjweqhfioranskdvnaeioghesdnjkznvkaj"+
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyqwsfhskdnfnalghsdaklfalghewklahfiojsdlf",
            roomId)
        self.assertEqual(
            answerOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            answerOverFlowInfo['message'],
            ESSAY_ANSWER_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerAddEssay(
            '', 'who is laughing?', 'genius', roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)

    # 【delEssay(); innerDel()】
    def test_del_essay(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        essays = Essay.objects.all()

        # 【delEssay()】
        # 正常删除
        response1 = self.client.post(
            '/ink/delEssay/?room=' + getEncodedRoomID(roomId), {'id': "essay_" + str(essays[1].id)})
        self.assertEqual(response1.status_code, 200)

        # 异常：错误url
        response2 = self.client.post('/delEssay/?room=' + getEncodedRoomID(roomId), {'id': "essay_" + str(essays[0].id)})
        self.assertEqual(response2.status_code, 404)

        # 【innerDel( type=essay )】
        # 正常删除
        successDelInfo = innerDel(
            'essay', "essay_" + str(essays[0].id), roomId)
        self.assertEqual(successDelInfo['status'], "success")
        self.assertEqual(successDelInfo['message'], u"删除简答题成功！")

        sodagreen = Essay.objects.filter(title='sodagreen')
        self.assertEqual(len(sodagreen), 0)

        # 异常：房间id不存在
        noRoomInfo = innerDel('Essay', "essay_" + str(essays[0].id), roomId+1)
        self.assertEqual(noRoomInfo['status'], "fail")
        self.assertEqual(noRoomInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：要删除的简答题id不存在
        noEssayId = innerDel('essay', "essay_" + str(essays[0].id+10), roomId)
        self.assertEqual(noEssayId['status'], "fail")
        self.assertEqual(noEssayId['message'], NO_SUCH_ID)

    # 【editEssay()】
    def test_edit_essay(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        essays = Essay.objects.all()

        # 正常编辑
        response1 = self.client.post('/ink/editEssay/?room=' + getEncodedRoomID(roomId),
                                     {'essayTitle': "hahaha",
                                      'essayStem': "who is laughing?",
                                      'essayAnswer': "genius",
                                      'essayId': "essay_"+str(essays[0].id)})
        self.assertEqual(response1.status_code, 200)
        try:
            Essay1 = Essay.objects.get(title="hahaha")
        except Essay.DoesNotExist:
            Essay1 = None
        if Essay1 is not None:
            self.assertEqual(Essay1.stem, "who is laughing?")
            self.assertEqual(Essay1.answer, "genius")

    # 【innerEditEssay()】
    def test_inner_edit_essay(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        Essays = Essay.objects.all()
        editId = "essay_"+str(Essays[0].id)

        # 正常编辑
        successEditEssayInfo = innerEditEssay(
            "ha", "who is laughing?", "genius", editId, roomId)
        self.assertEqual(successEditEssayInfo['status'], 'success')
        self.assertEqual(successEditEssayInfo['message'], u"编辑简答题成功！")
        self.assertEqual(Essays[0].title, "ha")

        # 异常：房间id不存在
        noRoomIdInfo = innerEditEssay(
            'no room id', 'nothing', 'answer', editId, roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerEditEssay(
            'iloveyou', 'nothing', 'sudasudalvlv!', editId, roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerEditEssay(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "sodagreen", editId, roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerEditEssay(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "awesome",
            editId,
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：简答答案溢出
        answerOverFlowInfo = innerEditEssay(
            "answerbomb",
            "[]",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyasdfgjweqhfioranskdvnaeioghesdnjkznvkaj"+
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyqwsfhskdnfnalghsdaklfalghewklahfiojsdlf",
            editId,
            roomId)
        self.assertEqual(
            answerOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            answerOverFlowInfo['message'],
            ESSAY_ANSWER_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerEditEssay(
            '', 'who is laughing?', 'april', editId, roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)


class CodeTestCase(TestCase):
    def setUp(self):
        interview = Interview.objects.create(
            name="unittest",
            startTime="2016-07-10 21:59",
            logo="logo.jpg"
        )
        Interviewer.objects.create(
            name="victor",
            email="yd-chen14@mails.tsinghua.edu.cn",
            interview=interview
        )
        Code.objects.create(
            title="sodagreen",
            stem="sodared",
            sampleInput="sodablue",
            sampleOutput="sodasky",
            interview=interview
        )
        Code.objects.create(
            title="iloveyou",
            stem="imustkeepsinging",
            sampleInput="icannotkeeptrying",
            sampleOutput="dying",
            interview=interview
        )
        Code.objects.create(
            title="everyone",
            stem="idoesntmatterifyoufeellikenothing",
            sampleInput="playingmusic",
            sampleOutput="sing it",
            interview=interview
        )

    # 【addCode()】
    def test_add_code(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        response1 = self.client.post('/ink/addCode/?room=' + getEncodedRoomID(roomId),
                                     {'codeTitle': "hahaha",
                                      'codeStem': "who is laughing?",
                                      'codeSampleInput': "genius",
                                      'codeSampleOutput': 'nothing'})
        self.assertEqual(response1.status_code, 200)
        try:
            code1 = Code.objects.get(title="hahaha")
        except Code.DoesNotExist:
            code1 = None
        if code1 is not None:
            self.assertEqual(code1.stem, "who is laughing?")
            self.assertEqual(code1.sampleInput, "genius")
            self.assertEqual(code1.sampleOutput, "nothing")

        # 异常：错误url
        response2 = self.client.post('/addCode/?room=' + getEncodedRoomID(roomId),
                                     {'codeTitle': "hahaha",
                                      'codeStem': "who is laughing?",
                                      'codeSampleInput': "genius",
                                      'codeSampleOutput': 'nothing'})
        self.assertEqual(response2.status_code, 404)

        # 异常：错误request key
        with self.assertRaises(KeyError):
            self.client.post('/ink/addCode/?room=' + getEncodedRoomID(roomId),
                             {'codeTitle': "hahahooo",
                              'codeStem': "who is laughing? lalalooo",
                              'sampleInput': "genius",
                              'sampleOutput': 'nothing'})

    # 【innerAddCode()】
    def test_inner_add_code(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        # 正常添加
        successAddCodeInfo = innerAddCode(
            "ha", "who is laughing?", "genius?", "fools", roomId)
        self.assertEqual(successAddCodeInfo['status'], 'success')
        self.assertEqual(successAddCodeInfo['message'], u"添加编程题成功！")

        # 异常：房间id不存在
        noRoomIdInfo = innerAddCode(
            'no room id', 'nothing', 'input', 'output', roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerAddCode(
            'iloveyou', 'nothing', 'collllllld!', 'ill', roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerAddCode(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "sodagreen", "right", roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerAddCode(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "awesome",
            "wangnima",
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：编程题样例输入溢出
        inputOverFlowInfo = innerAddCode(
            "inputbomb",
            "no!",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyasdfgjweqhfioranskdvnaeioghesdnjkznvkaj"+
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyqwsfhskdnfnalghsdaklfalghewklahfiojsdlf",
            "short",
            roomId)
        self.assertEqual(
            inputOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            inputOverFlowInfo['message'],
            SAMPLE_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerAddCode(
            '', 'who is laughing?', 'genius', 'NOTHING', roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)

    # 【delCode(); innerDel()】
    def test_del_code(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        codes = Code.objects.all()

        # 【delCode()】
        # 正常删除
        response1 = self.client.post(
            '/ink/delCode/?room=' + getEncodedRoomID(roomId), {'id': "code_" + str(codes[1].id)})
        self.assertEqual(response1.status_code, 200)

        # 异常：错误url
        response2 = self.client.post('/delCode/?room=' + getEncodedRoomID(roomId), {'id': "code_" + str(codes[0].id)})
        self.assertEqual(response2.status_code, 404)

        # 【innerDel( type=code )】
        # 正常删除
        successDelInfo = innerDel(
            'code', "code_" + str(codes[0].id), roomId)
        self.assertEqual(successDelInfo['status'], "success")
        self.assertEqual(successDelInfo['message'], u"删除编程题成功！")

        iloveyou = Code.objects.filter(title='iloveyou')
        self.assertEqual(len(iloveyou), 0)

        # 异常：房间id不存在
        noRoomInfo = innerDel('Code', "code_" + str(codes[0].id), roomId+1)
        self.assertEqual(noRoomInfo['status'], "fail")
        self.assertEqual(noRoomInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：要删除的简答题id不存在
        noCodeId = innerDel('Code', "code_" + str(codes[0].id+10), roomId)
        self.assertEqual(noCodeId['status'], "fail")
        self.assertEqual(noCodeId['message'], NO_SUCH_ID)

    # 【editCode()】
    def test_edit_code(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        codes = Code.objects.all()

        # 正常编辑
        response1 = self.client.post('/ink/editCode/?room=' + getEncodedRoomID(roomId),
                                     {'codeTitle': "hahaha",
                                      'codeStem': "who is laughing?",
                                      'codeSampleInput': "genius",
                                      'codeSampleOutput': "fool",
                                      'codeId': "code_"+str(codes[0].id)})
        self.assertEqual(response1.status_code, 200)
        try:
            Code1 = Code.objects.get(title="hahaha")
        except Code.DoesNotExist:
            Code1 = None
        if Code1 is not None:
            self.assertEqual(Code1.stem, "who is laughing?")
            self.assertEqual(Code1.sampleInput, "genius")
            self.assertEqual(Code1.sampleOutput, "fool")

    # 【innerEditCode()】
    def test_inner_edit_code(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        Codes = Code.objects.all()
        editId = "code_"+str(Codes[0].id)

        # 正常编辑
        successEditCodeInfo = innerEditCode(
            "ha", "who is laughing?", "genius", "fool", editId, roomId)
        self.assertEqual(successEditCodeInfo['status'], 'success')
        self.assertEqual(successEditCodeInfo['message'], u"编辑编程题成功！")
        self.assertEqual(Codes[0].title, "ha")

        # 异常：房间id不存在
        noRoomIdInfo = innerEditCode(
            'no room id', 'nothing', 'answer', 'output', editId, roomId + 1)
        self.assertEqual(noRoomIdInfo['status'], 'fail')
        self.assertEqual(noRoomIdInfo['message'], NO_SUCH_ROOM_ID)

        # 异常：标题重复
        reduplicativeTitleInfo = innerEditCode(
            'iloveyou', 'nothing', 'sudasudalvlv!', 'sudasudalv~lv~', editId, roomId)
        self.assertEqual(reduplicativeTitleInfo['status'], 'fail')
        self.assertEqual(
            reduplicativeTitleInfo['message'],
            REDUPLICATIVE_TITLE)

        # 异常：标题溢出
        titleOverFlowInfo = innerEditCode(
            "zheshiyishoujiandandexiaoqingge, changzhewomenxintoudequzhe",
            "who is singing?",
            "sodagreen", "e", editId, roomId)
        self.assertEqual(
            titleOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            titleOverFlowInfo['message'],
            TITLE_OVERFLOW)

        # 异常：题干溢出
        stemOverFlowInfo = innerEditCode(
            "stembomb",
            "As Python’s normal unittest.TestCase class implements assertion methods such as assertTrue() and assertEqual(), Django’s custom TestCase class provides a number of custom assertion methods that are useful for testing Web applications:The failure messages given by most of these assertion methods can be customized with the msg_prefix argument. This string will be prefixed to any failure message generated by the assertion. This allows you to provide additional details that may help you to identify the location and cause of an failure in your test suite.",
            "what dya feel?",
            "awesome",
            editId,
            roomId)
        self.assertEqual(
            stemOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            stemOverFlowInfo['message'],
            STEM_OVERFLOW)

        # 异常：样例输入溢出
        answerOverFlowInfo = innerEditCode(
            "answerbomb",
            "aaaa",
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyasdfgjweqhfioranskdvnaeioghesdnjkznvkaj"+
            "hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha hahahahahahaha hahahahaha aaaaaaa everydayicare everydayifeel everythatmomentisover everydayyoutrack everydayyousense whenyouwakeupthismorning youwillseeihavebeenstrangealreadyqwsfhskdnfnalghsdaklfalghewklahfiojsdlf",
            "imshort",
            editId,
            roomId)
        self.assertEqual(
            answerOverFlowInfo['status'],
            'fail')
        self.assertEqual(
            answerOverFlowInfo['message'],
            SAMPLE_OVERFLOW)

        # 异常：空输入
        emptyInputInfo = innerEditCode(
            '', 'who is laughing?', 'april', 'november', editId, roomId)
        self.assertEqual(emptyInputInfo['status'], 'fail')
        self.assertEqual(emptyInputInfo['message'], EMPTY_INPUT)


class SmallFunctionsTestCase(TestCase):
    def setUp(self):
        interview = Interview.objects.create(
            name="unittest",
            startTime="2016-07-10 21:59",
            logo="logo.jpg"
        )
        Interviewer.objects.create(
            name="victor",
            email="yd-chen14@mails.tsinghua.edu.cn",
            interview=interview
        )
        Candidate.objects.create(
            name="cyd",
            email="orangexyx@qq.com",
            phoneNumber="13111112222",
            interview=interview,
            state=0,
            videopath="/video",
            reportpath="/report",
            codepath="/code",
            whiteboardpath="/wb",
            chatpath="/chat"
        )
        Choice.objects.create(
            title="sodagreen",
            stem="which ones do you like?",
            optionA="spring",
            optionB="summer",
            optionC="autumn",
            optionD="winter",
            optionE="",
            optionF="",
            optionNum=4,
            answer="ABCD",
            interview=interview)
        Completion.objects.create(
            title="kiterunner",
            stem="what's wrong with the title?[]",
            answer="the",
            interview=interview)
        Essay.objects.create(
            title="soda",
            stem="when do you meet soda?",
            answer="2009",
            interview=interview)
        Code.objects.create(
            title="everyone",
            stem="idoesntmatterifyoufeellikenothing",
            sampleInput="playingmusic",
            sampleOutput="sing it",
            interview=interview
        )
        Code.objects.create(
            title="iloveyou",
            stem="imustkeepsinging",
            sampleInput="icannotkeeptrying",
            sampleOutput="dying",
            interview=interview
        )

    def test_get_success_info(self):
        self.assertEqual(getSuccessInfo(ADD, CHOICE), u"添加选择题成功！")
        self.assertEqual(getSuccessInfo(EDIT, CODE), u"编辑编程题成功！")
        self.assertEqual(getSuccessInfo(DEL, ESSAY), u"删除简答题成功！")

    def test_check_illegal_room_id(self):
        rooms = Interview.objects.all()
        legalRoomId = rooms[0].id
        illegalRoomId = rooms[0].id + 100
        self.assertEqual(checkIllegalRoomId(illegalRoomId), True)
        self.assertEqual(checkIllegalRoomId(legalRoomId), False)

    def test_get_options_in_jsend(self):
        op = ["soda1", "soda2", "soda3", "soda4", "", ""]
        self.assertEqual(getOptionsInJsend(op), ["A.soda1", "B.soda2", "C.soda3", "D.soda4"])

    def test_check__option_empty(self):
        op1 = ["soda1", "soda2", "soda3", "soda4", "", ""]
        op2 = ["soda1", "", "soda3", "soda4", "", ""]
        opNum = "4"
        self.assertEqual(checkOptionEmpty(op1, opNum), False)
        self.assertEqual(checkOptionEmpty(op2, opNum), True)

    def test_check_illegal_answer(self):
        opNum = "4"
        answer1 = "CDE"
        answer2 = "AB"
        answer3 = "Gg"
        self.assertEqual(checkIllegalAnswer(opNum, answer1), True)
        self.assertEqual(checkIllegalAnswer(opNum, answer2), False)
        self.assertEqual(checkIllegalAnswer(opNum, answer3), True)

    def test_check_reduplicative_options(self):
        op1 = ["soda1", "soda2", "soda3", "soda4", "", ""]
        op2 = ["soda1", "soda1", "soda3", "soda4", "", ""]
        opNum = "4"
        self.assertEqual(checkReduplicativeOptions(op1, opNum), False)
        self.assertEqual(checkReduplicativeOptions(op2, opNum), True)

    def test_check_reduplicative_title_in_add(self):
        newtitle = "sodagreen"
        self.assertEqual(checkReduplicativeTitleInAdd('choice', newtitle), True)
        self.assertEqual(checkReduplicativeTitleInAdd('essay', newtitle), False)

    def test_check_reduplicative_title_in_edit(self):
        newtitle1 = "everyone"
        newtitle2 = "iloveyou"
        theId = Code.objects.all()[0].id
        self.assertEqual(checkReduplicativeTitleInEdit('code', newtitle1, theId), False)
        self.assertEqual(checkReduplicativeTitleInEdit('code', newtitle2, theId), True)

    def test_get_imgurls_in_richtext(self):
        stem = '<img alt="1.jpg" src="/static/media/1.jpg" height="220" width="217">' \
               '<img alt="2.jpg" src="/static/media/2.jpg" height="220" width="217">'
        imgurls = [BASE_DIR+"/static/media/1.jpg", BASE_DIR+"/static/media/2.jpg"]
        self.assertEqual(getImgUrlsInRichText(stem), imgurls)

    def test_BKDR_hash(self):
        email1 = "yd-chen14@mails.tsinghua.edu.cn"
        email2 = "529641713@qq.com"
        self.assertEqual(BKDRHash(email1), 480801869)
        self.assertEqual(BKDRHash(email2), 1718126729)

    def test_get_encoded_roomId(self):
        rooms = Interview.objects.all()
        roomId = rooms[0].id
        self.assertEqual(getEncodedRoomID(roomId), "480801869_"+str(roomId))
        self.assertEqual(getEncodedRoomID(roomId+7), "no_such_id")

    def test_check_illegal_encoded_roomId(self):
        rooms = Interview.objects.all()
        roomId = rooms[0].id
        legalEncodedRoomId = "480801869_" + str(roomId)
        illegalEncodedRoomId1 = "480801869_" + str(roomId + 1)
        illegalEncodedRoomId2 = "48080186abc_" + str(roomId)
        self.assertEqual(checkIllegalEncodedRoomID(legalEncodedRoomId), False)
        self.assertEqual(checkIllegalEncodedRoomID(illegalEncodedRoomId1), True)
        self.assertEqual(checkIllegalEncodedRoomID(illegalEncodedRoomId2), True)


    # Add in Nov. 30th
    def test_show_interviewee(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        response1 = self.client.post('/ink/intervieweeManage/?room=' + getEncodedRoomID(roomId))
        self.assertEqual(response1.status_code, 200)

    def test_get_question_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        response1 = self.client.post('/ink/problems/?room=' + getEncodedRoomID(roomId))
        self.assertEqual(response1.status_code, 200)

    def test_get_choicelist_in_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        choiceRet = getChoiceListInJsend(roomId, 1)
        self.assertEqual(choiceRet['mark'], 2)
        self.assertEqual(choiceRet['choiceList'][0]['type'], "choice")

    def test_get_completionlist_in_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        completionRet = getCompletionListInJsend(roomId, 1)
        self.assertEqual(completionRet['mark'], 2)
        self.assertEqual(completionRet['completionList'][0]['type'], "completion")

    def test_get_essaylist_in_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        essayRet = getEssayListInJsend(roomId, 1)
        self.assertEqual(essayRet['mark'], 2)
        self.assertEqual(essayRet['essayList'][0]['type'], "essay")

    def test_get_codelist_in_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        codeRet = getCodeListInJsend(roomId, 1)
        self.assertEqual(codeRet['mark'], 3)
        self.assertEqual(codeRet['codeList'][0]['type'], "code")

    def test_get_candidate_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        response1 = self.client.post('/ink/getCandidate/?room=' + getEncodedRoomID(roomId))
        self.assertEqual(response1.status_code, 200)

    def test_get_room_jsend(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        response1 = self.client.post('/ink/getRoomId/?room=' + getEncodedRoomID(roomId))
        self.assertEqual(response1.status_code, 200)

    def test_show_questions(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id

        response1 = self.client.post('/ink/interviewerManage/?room=' + getEncodedRoomID(roomId))
        self.assertEqual(response1.status_code, 200)

    def test_get_choice_by_id(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        choices = Choice.objects.all()
        theId = str(choices[0].id)

        response1 = self.client.post('/ink/getChoiceById/?room=' + getEncodedRoomID(roomId),
                                     {'choiceId': "choice_" + theId})
        self.assertEqual(response1.status_code, 200)

    def test_get_completion_by_id(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        completions = Completion.objects.all()
        theId = str(completions[0].id)

        response1 = self.client.get('/ink/getCompletionById/?room=' + getEncodedRoomID(roomId),
                                    {'completionId': "completion_" + theId})
        self.assertEqual(response1.status_code, 200)

    def test_get_essay_by_id(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        essays = Essay.objects.all()
        theId = str(essays[0].id)

        response1 = self.client.get('/ink/getEssayById/?room=' + getEncodedRoomID(roomId),
                                    {'essayId': "essay_" + theId})
        self.assertEqual(response1.status_code, 200)

    def test_get_code_by_id(self):

        room = Interview.objects.filter(name="unittest")
        roomId = room[0].id
        codes = Code.objects.all()
        theId = str(codes[0].id)

        response1 = self.client.get('/ink/getCodeById/?room=' + getEncodedRoomID(roomId),
                                    {'codeId': "code_" + theId})
        self.assertEqual(response1.status_code, 200)

    def test_file_upload(self):

        response1 = self.client.get('/ink/fileUpload/', {'upload_file': "1.jpg"})
        self.assertEqual(response1.status_code, 200)

    def test_get_status_after_interview(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/getStatusAfterInterview/',
                                    {'candidate': canId, 'status': '2'})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(candidates[0].state, 2)

    def test_get_filepath_after_interview(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/getFilepathAfterInterview/',
                                    {'candidate': canId,
                                     'videopath': "/v1.wav",
                                     'reportpath': "/r1.txt",
                                     'codepath': "/c1.txt",
                                     'whiteboardpath': "/wb1.txt",
                                     'chatpath': "/ch1.txt"})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(candidates[0].chatpath, "/ch1.txt")

    def test_check_video_filepath(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/checkVideoFilepath/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_download_video(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/downloadVideo/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_check_report_filepath(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/checkReportFilepath/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_download_report(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/downloadReport/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_check_finalcode_filepath(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/checkFinalcodeFilepath/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_download_finalcode(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/downloadFinalcode/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_check_whiteboard_filepath(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/checkWhiteboardFilepath/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_download_whiteboard(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/downloadWhiteboard/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_check_chat_filepath(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/checkChatFilepath/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)

    def test_download_chat(self):

        candidates = Candidate.objects.all()
        canId = str(candidates[0].id)

        response1 = self.client.get('/ink/downloadChat/',
                                    {'intervieweeId': canId})
        self.assertEqual(response1.status_code, 200)






