/**
 * Created by chen on 2016/10/29.
 */

$(document).ready(function () {
    var addEssayEditor = new Simditor({
        textarea: $('#essayStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
        pasteImage: true,
    });

    var editEssayEditor = new Simditor({
        textarea: $('#editEssayStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
    });
    //"添加题目"按钮点击时的反应
    $("#addEssayButton").click(function () {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#essay").modal('show');
    })

    //点击题目的反应
    // $("td.tdEssayName").click(function () {
    //    // $("#editCodeSave").attr('name',$(this).attr('name'));
    //     $.get("/ink/getEssayById/",{'EssayId': $(this).attr('name')}, function(ret) {
    //         $("#editEssayTitle").val(ret.title);
    //         $("#editEssayStem").val(ret.stem);
    //         $("#editEssayAnswer").val(ret.answer);
    //         $("#editEssay").attr('readonly','readonly');
    //         $("#editEssay").modal('show');
    //     });
    // })

    //点击删除按钮的反应
    $('button.essayDel').unbind();
    $('button.essayDel').bind('click', function(e) {
        e.preventDefault();
        var questionId = $(this).attr('name');
        Confirm.show('确认删除', '确定要删除这道题吗?', {
            'Delete': {
                'primary': true,
                'callback': function() {
                    $("#checkDel").remove();
                    $.ajaxSetup({
                        headers: {"X-CSRFToken": getCookie("csrftoken")}
                    });
                    $.post("/ink/delEssay/?room="+$("#roomId").val(), {'id': questionId},function (ret) {
                    if(ret.status == "success") {
                        initToastr();
                        var $toast = toastr['success']('删除成功');
                    }
                    else {
                        initToastr();
                        var $toast = toastr['error'](ret.message);
                    }
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);
                    });
                }
            }
        });
    });

    //点击添加题目模态框保存按钮的反应
    $("#essaySave").click(function () {
        var essayTitle = $("#essayTitle").val();
        var essayStem = addEssayEditor.getValue();
        var essayAnswer = $("#essayAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/addEssay/?room='+$("#roomId").val(),
            {
                'essayTitle': essayTitle,
                'essayStem': essayStem,
                'essayAnswer': essayAnswer,
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#essayTitle").val("");
                    $("#essay textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

    //"编辑"按钮被点击时的响应
    $("button.essayEdit").click(function() {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#editEssaySave").attr('name',$(this).attr('name'));
        $.get("/ink/getEssayById/?room="+$("#roomId").val(),{'essayId': $(this).attr('name')}, function(ret) {
            $("#editEssayTitle").val(ret.title);
            editEssayEditor.setValue(ret.stem);
            //$("#editEssayStem").setValue(ret.stem);
            $("#editEssayAnswer").val(ret.answer);
            $("#editEssay").modal('show');
        });
    });

    //点击编辑模态框保存按钮的反应
    $("#editEssaySave").click(function () {
        var essayTitle = $("#editEssayTitle").val();
        var essayStem = editEssayEditor.getValue();
        var essayAnswer = $("#editEssayAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/editEssay/?room='+$("#roomId").val(),
            {
                'essayTitle': essayTitle,
                'essayStem': essayStem,
                'essayAnswer': essayAnswer,
                'essayId': $("#editEssaySave").attr('name'),
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('编辑成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#editEssayTitle").val("");
                    $("#editEssay textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

})
