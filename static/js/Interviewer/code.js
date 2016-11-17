/**
 * Created by chen on 2016/10/29.
 */

$(document).ready(function () {
    var addCodeEditor = new Simditor({
        textarea: $('#codeStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
        pasteImage: true,
    });
    var editCodeEditor = new Simditor({
        textarea: $('#editCodeStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
    });
    //"添加题目"按钮点击时的反应
    $("#addCodeButton").click(function () {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#code").modal('show');
    })
    
    //点击题目的反应
    // $("td.tdCodeName").click(function () {
    //    // $("#editCodeSave").attr('name',$(this).attr('name'));
    //     $.get("/ink/getCodeById/",{'CodeId': $(this).attr('name')}, function(ret) {
    //         $("#editCodeTitle").val(ret.title);
    //         $("#editCodeStem").val(ret.stem);
    //         $("#editCodeAnswer").val(ret.answer);
    //         $("#editCode").attr('readonly','readonly');
    //         $("#editCode").modal('show');
    //     });
    // })
    
    //点击删除按钮的反应
    $('button.codeDel').unbind();
    $('button.codeDel').bind('click', function(e) {
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
                    $.post("/ink/delCode/?room="+$("#roomId").val(), {'id': questionId},function (ret) {
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
    $("#codeSave").click(function () {
        var codeTitle = $("#codeTitle").val();
        var codeStem = addCodeEditor.getValue();
        var codeSampleInput = $("#codeSampleInput").val();
        var codeSampleOutput = $("#codeSampleOutput").val();

        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        
        $.post('/ink/addCode/?room='+$("#roomId").val(),
            {
                'codeTitle': codeTitle,
                'codeStem': codeStem,
                'codeSampleInput': codeSampleInput,
                'codeSampleOutput': codeSampleOutput,
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#codeTitle").val("");
                    $("#code textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

    //"编辑"按钮被点击时的响应
    $("button.codeEdit").click(function() {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#editCodeSave").attr('name',$(this).attr('name'));
        $.get("/ink/getCodeById/?room="+$("#roomId").val(),{'codeId': $(this).attr('name')}, function(ret) {
            $("#editCodeTitle").val(ret.title);
            editCodeEditor.setValue(ret.stem);
            $("#editCodeSampleInput").val(ret.sampleInput);
            $("#editCodeSampleOutput").val(ret.sampleOutput);
            $("#editCode").modal('show');
        });
    });

    //点击编辑模态框保存按钮的反应
    $("#editCodeSave").click(function () {
        var codeTitle = $("#editCodeTitle").val();
        var codeStem = editCodeEditor.getValue();
        var codeSampleInput = $("#editCodeSampleInput").val();
        var codeSampleOutput = $("#editCodeSampleOutput").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/editCode/?room='+$("#roomId").val(),
            {
                'codeTitle': codeTitle,
                'codeStem': codeStem,
                'codeSampleInput': codeSampleInput,
                'codeSampleOutput': codeSampleOutput,
                'codeId': $("#editCodeSave").attr('name'),
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('编辑成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#editCodeTitle").val("");
                    $("#editCode textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

})






