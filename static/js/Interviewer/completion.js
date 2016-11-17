/**
 * Created by chen on 2016/10/29.
 */

$(document).ready(function () {
    var addCompletionEditor = new Simditor({
        textarea: $('#completionStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
        pasteImage: true,
    });
    var editCompletionEditor = new Simditor({
        textarea: $('#editCompletionStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
    });
    //"添加题目"按钮点击时的反应
    $("#addCompletionButton").click(function () {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#completion").modal('show');
    })
    
    //点击题目的反应
    // $("td.tdCompletionName").click(function () {
    //    // $("#editCodeSave").attr('name',$(this).attr('name'));
    //     $.get("/ink/getCompletionById/",{'CompletionId': $(this).attr('name')}, function(ret) {
    //         $("#editCompletionTitle").val(ret.title);
    //         $("#editCompletionStem").val(ret.stem);
    //         $("#editCompletionAnswer").val(ret.answer);
    //         $("#editCompletion").attr('readonly','readonly');
    //         $("#editCompletion").modal('show');
    //     });
    // })
    
    //点击删除按钮的反应
    $('button.completionDel').unbind();
    $('button.completionDel').bind('click', function(e) {
        e.preventDefault();
        var questionId = $(this).attr('name');
        Confirm.show('确认删除', '确定要删除这道题吗?', {
            'Delete': {
                'primary': true,
                'callback': function () {
                    $("#checkDel").remove();
                    $.ajaxSetup({
                        headers: {"X-CSRFToken": getCookie("csrftoken")}
                    });
                    $.post("/ink/delCompletion/?room="+$("#roomId").val(), {'id': questionId},function (ret) {
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
        })
    });

    //点击添加题目模态框保存按钮的反应
    $("#completionSave").click(function () {
        var completionTitle = $("#completionTitle").val();
        var completionStem = addCompletionEditor.getValue();
        var completionAnswer = $("#completionAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/addCompletion/?room='+$("#roomId").val(),
            {
                'completionTitle': completionTitle,
                'completionStem': completionStem,
                'completionAnswer': completionAnswer,
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#completionTitle").val("");
                    $("#completion textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

    //"编辑"按钮被点击时的响应
    $("button.completionEdit").click(function() {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#editCompletionSave").attr('name',$(this).attr('name'));
        $.get("/ink/getCompletionById/?room="+$("#roomId").val(),{'completionId': $(this).attr('name')}, function(ret) {
            $("#editCompletionTitle").val(ret.title);
            editCompletionEditor.setValue(ret.stem);
            $("#editCompletionAnswer").val(ret.answer);
            $("#editCompletion").modal('show');
        });
    });

    //点击编辑模态框保存按钮的反应
    $("#editCompletionSave").click(function () {
        var completionTitle = $("#editCompletionTitle").val();
        var completionStem = editCompletionEditor.getValue();
        var completionAnswer = $("#editCompletionAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/editCompletion/?room='+$("#roomId").val(),
            {
                'completionTitle': completionTitle,
                'completionStem': completionStem,
                'completionAnswer': completionAnswer,
                'completionId': $("#editCompletionSave").attr('name'),
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('编辑成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#editCompletionTitle").val("");
                    $("#editCompletion textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

})