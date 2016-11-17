$(document).ready(function() {
     //下载视频录像
    $("button.videoRecord").click(function () {
        var interviewerId = $(this).attr('name');
        $.get("/ink/checkVideoFilepath/?room="+$("#roomId").val(),{'intervieweeId': $(this).attr('name')}, function(ret) {
            if(ret.status=="success")
            {
                download('/ink/downloadVideo/', interviewerId);
            }
            else
                Confirm.show('提示', ret.message);
        });
    })

    //下载白板记录
    $("button.whiteBoardRecord").click(function () {
        var interviewerId = $(this).attr('name');
        $.get("/ink/checkWhiteboardFilepath/?room="+$("#roomId").val(),{'intervieweeId': $(this).attr('name')}, function(ret) {
            if(ret.status=="success")
            {
                download('/ink/downloadWhiteboard/', interviewerId);
            }
            else
                Confirm.show('提示', ret.message);
        });
    })

    // 下载代码协同编辑记录
    $("button.codeEditRecord").click(function () {
        var interviewerId = $(this).attr('name');
        $.get("/ink/checkFinalcodeFilepath/?room="+$("#roomId").val(),{'intervieweeId': $(this).attr('name')}, function(ret) {
            if(ret.status=="success")
            {
                download('/ink/downloadFinalcode/', interviewerId);
            }
            else
                Confirm.show('提示', ret.message);
        });
    })

    // 下载聊天室记录
    $("button.chatRecord").click(function () {
        var interviewerId = $(this).attr('name');
        $.get("/ink/checkChatFilepath/?room="+$("#roomId").val(),{'intervieweeId': $(this).attr('name')}, function(ret) {
            if(ret.status=="success")
            {
                download('/ink/downloadChat/', interviewerId);
            }
            else
                Confirm.show('提示', ret.message);
        });
    })

    // 下载面试报告
    $("button.interviewReport").click(function () {
        var interviewerId = $(this).attr('name');
        $.get("/ink/checkReportFilepath/?room="+$("#roomId").val(),{'intervieweeId': $(this).attr('name')}, function(ret) {
            if(ret.status=="success")
            {
                download('/ink/downloadReport/', interviewerId);
            }
            else
                Confirm.show('提示', ret.message);
        });
    })


    //"添加候选人"模态框保存按钮点击时的响应
    $("#addCandidateSave").click(function () {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        var candidateName = $("#addCandidate_nameInput").val();
        var email = $("#addCandidate_emailInput").val();
        var phoneNumber = $("#addCandidate_phoneNumberInput").val();

        var x = document.getElementById("myRoom").selectedIndex;
        var y = document.getElementById("myRoom").options;
        var roomName = y[x].text;

        $("div.loading").removeClass('hidden');

        $.post("/ink/addCandidate/", {'candidateName': candidateName, 'email': email,
            'phoneNumber': phoneNumber, 'interviewName': roomName}, function(ret){
            if (ret.status == 'success') {
                initToastr();
                var $toast = toastr['success']('添加成功');
                $("#rightPanel").html(ret.pageText);
                $("div.modal-backdrop").remove();
            }
            else {
                Confirm.show('提示', ret.message);
                $("div.loading").addClass('hidden');
            }
         });
    });

    //"编辑候选人"按钮被点击时的响应
    $("button.editCandidateInfo").click(function() {
        var theId = ($(this).attr('name'));
        var theInfoLine = new Array();
        $("td[name=\'"+theId+"\']").each(function(){
            theInfoLine.push($(this).html());
        });

        var editInputs = new Array();
        $("#editCandidateModalBody input").each(function(){
            editInputs.push($(this));
        });

        for(var i = 0; i < 3 ; i++) {
            editInputs[i].attr('value', theInfoLine[i]);
        }

        var roomInput = theInfoLine[3];

        var obj = document.getElementById('interviewName');
        for(var j = 0; ; j++) {
            if(obj.options[j].value == roomInput) {
                obj.options[j].selected = true;
                break;
            }
        }
        $("#editCandidateSave").attr('name', theId); //在编辑房间"保存"按钮的name属性上存下该表行的id，给views.py中的editRoom函数做铺垫
        $("#editCandidateModal").modal('show');
    });

    //"编辑候选人"模态框保存按钮点击时的响应
    $("#editCandidateSave").click(function () {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });

        var candidateName = $("#editCandidate_nameInput").val();
        var candidateEmail = $("#editCandidate_emailInput").val();
        var phoneNumber = $("#editCandidate_phoneNumberInput").val();
        var x = document.getElementById("interviewName").selectedIndex;
        var y = document.getElementById("interviewName").options;
        var roomName = y[x].text;

        var id = ($(this).attr('name'));

        $("div.loading").removeClass('hidden');

        $.post("/ink/editCandidate/", {'candidateName': candidateName, 'email': candidateEmail,
            'phoneNumber': phoneNumber, 'interviewName': roomName, 'id': id}, function(ret){
            if (ret.status == 'success') {
                initToastr();
                var $toast = toastr['success']('修改成功');
                $("#rightPanel").html(ret.pageText);
                $("div.modal-backdrop").remove();
            }
            else {
                Confirm.show('提示', ret.message);
                $("div.loading").addClass('hidden');
            }
         });
    });

    //"删除候选人"按钮被点击时的响应
    $("button.deleteCandidate").click(function() {
        var id = ($(this).attr('name'));
        Confirm.show('', '确定要删除该候选人吗?', {'Delete': {
        'primary': true,
        'callback': function () {
             $.ajaxSetup({
                 headers: { "X-CSRFToken": getCookie("csrftoken") }
             });
            $.post("/ink/delCandidate/", {'id': id}, function(ret){
                if (ret.status == 'success') {
                    initToastr();
                    var $toast = toastr['success']('删除成功');
                    $("#rightPanel").html(ret.pageText);
                }
            });
            Confirm.hide();
        }
        }
        })


    });

    //"发送邮件给候选人"按钮被点击时的响应
    $("button.sendEmailToCandidate").click(function() {
        var theId = ($(this).attr('name'));
        var theInfoLine = new Array();
        $("td[name=\'"+theId+"\']").each(function(){
            theInfoLine.push($(this).html());
        });


        var sendEmailInputs = new Array();
        $("#sendEmailToCandidateModalBody input").each(function(){
            sendEmailInputs.push($(this));
        });
        sendEmailInputs[0].attr('value', theInfoLine[0]); //候选人姓名
        sendEmailInputs[1].attr('value', theInfoLine[1]); //收件人邮箱

        var emailContext = theInfoLine[0] + "您好！您参加的【" + theInfoLine[3] + "】面试开始时间为：，点击链接进入房间：";
        $.get("/ink/getCandidateURL/",{'candidateId':theId}, function(ret) {
            sendEmailInputs[2].attr('value', emailContext + ret);
        });

        $("#sendEmailToCandidateSave").attr('name', theId);    //在编辑房间"保存"按钮的name属性上存下该表行的id，给views.py中的editRoom函数做铺垫
        $("#sendEmailToCandidateModal").modal('show');
    });


    //"发送邮件给候选人 发送"按钮被点击时的响应
    $("#sendEmailToCandidateSave").click(function() {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        var name = $("#sendEmail_name").val();
        var email = $("#sendEmail_candidateEmail").val();
        var emailContext = $("#sendEmailToCandidate_emailContext").val();

        $("div.loading").removeClass('hidden');

        $.post("/ink/sendEmailToCandidate/", {'candidateName': name,
        'candidateEmail': email, 'emailContext': emailContext}, function(ret){
            if (ret.status == 'success') {
                initToastr();
                var $toast = toastr['success']('发送成功');
                $("#sendEmailToCandidateModal").hide();
                $("div.modal-backdrop").remove();
                $("div.loading").addClass('hidden');
            }
            else {
                Confirm.show('提示', ret.message);
                $("div.loading").addClass('hidden');
            }
        });
    });

    //"批量添加候选人 导入"按钮被点击时响应
    $("#addBatchCandidateSave").click(function() {
        $("div.loading").removeClass('hidden');

        $.ajaxFileUpload({
            url: "/ink/batchImportCandidate/",
            type: "POST",
            data: {'id': 1},
            secureuri: false,
            fileElementId: "excelfile",
            dataType: 'application/json',
            success: function(ret){
                //回调函数
                res = jQuery.parseJSON(jQuery(ret).text());
                if (res.status == 'success') {
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                    $("#rightPanel").html(res.pageText);
                    $("div.modal-backdrop").remove();
                }
                else {
                    Confirm.show('提示', res.message);
                    $("div.loading").addClass('hidden');
                }
            }
        });

    });
});
