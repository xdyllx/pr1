$(document).ready(function() {
    //"创建房间"模态框保存按钮点击时的响应
    $("#addRoomSave").click(function () {
        var roomName = $("#addRoom_nameInput").val();
        var interviewerName = $("#addRoom_interviewerNameInput").val();
        var interviewerEmail = $("#addRoom_interviewerEmailInput").val();
        var interviewStartTime = $("#addRoom_interviewStartTimeInput").val();

        $("div.loading").removeClass('hidden');


        $.ajaxFileUpload({
            url: "/ink/addRoom/",
            type: "POST",
            data: {'roomName': roomName,
            'starttime': interviewStartTime, 'interviewerName': interviewerName,
            'interviewerEmail': interviewerEmail},
            secureuri: false,
            fileElementId: 'addRoom_logoInput',
            dataType: "application/json",
            success: function(ret){
                //回调函数
                res = jQuery.parseJSON(jQuery(ret).text());
                if (res.status == 'success') {
                    $("#rightPanel").html(res.pageText);
                    $("div.modal-backdrop").remove();
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                }
                else {
                    Confirm.show('提示', res.message);
                    $("div.loading").addClass('hidden');
                }
            }
        });
    });

    //"编辑房间"按钮被点击时的响应
    $("button.editRoomInfo").click(function() {
        var theId = ($(this).attr('name'));
        var theInfoLine = new Array();
        $("td[name=\'"+theId+"\']").each(function(){
            theInfoLine.push($(this).html());
        });

        theInfoLine[0] = theInfoLine[0].substr(0,17)+"2"+theInfoLine[0].substr(18);
        var editInputs = new Array();
        $("#editRoomModalBody input").each(function(){
            editInputs.push($(this));
        });

        var prevDiv = document.getElementById('editpreview');
        prevDiv.innerHTML = theInfoLine[0];

        for(var i = 0; i < 4 ; i++) {
            editInputs[i].attr('value', theInfoLine[i+1]);
        }

        $("#editRoomSave").attr('name', theId); //在编辑房间"保存"按钮的name属性上存下该表行的id，给views.py中的editRoom函数做铺垫
        $("#editRoomModal").modal('show');
    });

    //"编辑房间信息"模态框保存按钮点击时的响应
    $("#editRoomSave").click(function () {
        var roomName = $("#editRoom_nameInput").val();
        var interviewerName = $("#editRoom_interviewerNameInput").val();
        var interviewerEmail = $("#editRoom_interviewerEmailInput").val();
        var interviewStartTime = $("#editRoom_interviewStartTimeInput").val();
        //var logo = $("#editRoom_logoInput").val();
        var id = ($(this).attr('name'));

        $("div.loading").removeClass('hidden');

        $.ajaxFileUpload({
                url: "/ink/editRoom/",
                type: "POST",
                data: {'roomName': roomName,
                'interviewStartTime': interviewStartTime, 'interviewerName': interviewerName,
                'interviewerEmail': interviewerEmail, 'id': id},
                secureuri: false,
                fileElementId: 'editRoom_logoInput',
                dataType: "application/json",
                success: function(ret){
                    //回调函数
                    res = jQuery.parseJSON(jQuery(ret).text());
                    if (res.status == 'success') {
                        initToastr();
                        var $toast = toastr['success']('修改成功');
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

    //"删除房间"按钮被点击时的响应
    $("button.deleteRoom").click(function() {
        var id = ($(this).attr('name'));
        Confirm.show('', '确定要删除该房间吗?', {'Delete': {
        'primary': true,
        'callback': function () {
            $.ajaxSetup({
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            });
            $.post("/ink/delRoom/", {'id': id}, function(ret){
                $("#rightPanel").html(ret.pageText);
                if (ret.status == 'success') {
                    initToastr();
                    var $toast = toastr['success']('删除成功');
                }
            });
            Confirm.hide();
        }
        }
        })
    });


    //"发送邮件给主考官"按钮被点击时的响应
    $("button.sendEmailToInterviewer").click(function() {
        var theId = ($(this).attr('name')); //面试官id
        var theInfoLine = new Array();
        $("td[name=\'"+theId+"\']").each(function(){
            theInfoLine.push($(this).html());
        });

        theInfoLine[1] = theInfoLine[1] + "面试：邀您做面试官"
        theInfoLine[2] = theInfoLine[2];  //面试官姓名
        theInfoLine[3] = theInfoLine[3];  //面试官邮箱
        theInfoLine[4] = theInfoLine[4];  //面试开始时间

        var sendEmailInputs = new Array();
        $("#sendEmailToInterviewerModalBody input").each(function(){
            sendEmailInputs.push($(this));
        });

        sendEmailInputs[0].attr('value', theInfoLine[1]); //房间名
        sendEmailInputs[1].attr('value', theInfoLine[3]); //收件人邮箱

        var emailContext = theInfoLine[2] + "您好！" + "面试开始时间为："+ theInfoLine[4] + "，点击链接进入房间：";

        $.get("/ink/getInterviewerURL/",{'interviewerId':theId}, function(ret) {
            sendEmailInputs[2].attr('value', emailContext + ret);
        });

        $("#sendEmailToInterviewerSave").attr('name', theId);    //在编辑房间"保存"按钮的name属性上存下该表行的id，给views.py中的editRoom函数做铺垫
        $("#sendEmailToInterviewerModal").modal('show');
    });


    //"发送邮件给主考官发送"按钮被点击时的响应
    $("#sendEmailToInterviewerSave").click(function() {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        var roomName = $("#sendEmail_roomName").val();
        var interviewerEmail = $("#sendEmail_interviewerEmail").val();
        var emailContext = $("#sendEmailToInterviewer_emailContext").val();

        $("div.loading").removeClass('hidden');

        $.post("/ink/sendEmailToInterviewer/", {'roomName': roomName,
        'interviewerEmail': interviewerEmail, 'emailContext': emailContext}, function(ret){
            if (ret.status == 'success') {
                initToastr();
                var $toast = toastr['success']('发送成功');
                $("#rightPanel").html(ret.pageText);
                //$("#sendEmailToInterviewerModal").hide();
                $("div.modal-backdrop").remove();
                $("div.loading").addClass('hidden');
            }
            else {
                Confirm.show('提示', res.message);
                $("div.loading").addClass('hidden');
            }
        });
    });

    //timepicker
    $('.form_datetime').datetimepicker({
        language:  'zh-CN',
        format: "yyyy-mm-dd hh:ii",
        //pick12HourFormat: 0,
        weekStart: 1,
        todayBtn:  1,
        autoclose: 1,
        todayHighlight: 1,
        startView: 2,
        forceParse: 0,
        showMeridian: 1
    });
});

function preview(file)
{
    var prevDiv = document.getElementById('preview');
    if (file.files && file.files[0]) {
        var reader = new FileReader();
        reader.onload = function(evt){
            var index1 = evt.target.result.indexOf('/') + 1;
            var index2 = evt.target.result.indexOf(';');
            var extension = evt.target.result.substring(index1, index2);
            extension = extension.toLowerCase();
            var png = "png"; var jpeg = "jpeg"; var jpg = "jpeg";
            if ((extension != png) && (extension != jpeg) && (extension != jpg))
                alert("图片格式不正确\n请上传.png, .jpg, .jpeg格式的图片");
            prevDiv.innerHTML = '<img class="image2" src="' + evt.target.result + '"/>';
        };
        reader.readAsDataURL(file.files[0]);
    }
    else {
        prevDiv.innerHTML = '<div class="img" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale,src=\'' + file.value + '\'"></div>';
    }
}



function editpreview(file) {
    var prevDiv = document.getElementById('editpreview');
    if (file.files && file.files[0]) {
        var reader = new FileReader();
        reader.onload = function(evt){
            var index1 = evt.target.result.indexOf('/') + 1;
            var index2 = evt.target.result.indexOf(';');
            var extension = evt.target.result.substring(index1, index2);
            extension = extension.toLowerCase();
            var png = "png"; var jpeg = "jpeg"; var jpg = "jpeg";
            if ((extension != png) && (extension != jpeg) && (extension != jpg))
                alert("图片格式不正确\n请上传.png, .jpg, .jpeg格式的图片");
            prevDiv.innerHTML = '<img class="image2" src="' + evt.target.result + '" />';
        };
        reader.readAsDataURL(file.files[0]);
    }
    else {
        prevDiv.innerHTML = '<div class="img" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale,src=\'' + file.value + '\'"></div>';
    }
}
