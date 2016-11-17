/**
 * Created by chen on 2016/10/29.
 */

$(document).ready(function () {
    var addChoiceEditor = new Simditor({
        textarea: $('#choiceStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
        pasteImage: true,
    });
    var editChoiceEditor = new Simditor({
        textarea: $('#editChoiceStem'),
        upload: {
            url : '/ink/fileUpload/', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'upload_file', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件',
        },
    });
    //"添加题目"按钮点击时的反应
    $("#addChoiceButton").click(function () {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#choice").modal('show');
    })
    
    var num = 0;

    //“添加选择题选项”按钮被点击时的反应
    $("#addOptionButton").click(function () {
        if(num > 5)
        {
            initToastr();
            var $toast = toastr['error']("最多设置六个选项");
        }
        else
        {
            num ++;
            var div = $("<div class = \"input-group optionDiv\"></div>").appendTo($("#optionsDiv"));
            var left = $("<span class = \"input-group-addon\"></span>").appendTo(div);
            if($("#addOptionCheckbox").prop('checked'))
            //var checkbox = $("<input type = \"checkbox\" id = \"checkbox" + option + "\" checked = \"" + $("#addOptionCheckbox").attr('checked') + "\">").appendTo(left);
                var checkbox = $("<input type = \"checkbox\" checked = \"true\">").appendTo(left);
            else
                var checkbox = $("<input type = \"checkbox\">").appendTo(left);
            var text = $("<input type = \"text\" class = \"form-control\" value = \"" + $("#addOptionText").val() + "\">").appendTo(div);
            var right = $("<span class = \"input-group-addon optionDel\">移除</span>").appendTo(div);

            //“移除”按钮被点击的反应
            right.click(function () {
                num --;
                div.remove();
            });
        }
    })
    
    //点击题目的反应
    // $("td.tdChoiceName").click(function () {
    //    // $("#editCodeSave").attr('name',$(this).attr('name'));
    //     $.get("/ink/getChoiceById/",{'ChoiceId': $(this).attr('name')}, function(ret) {
    //         $("#editChoiceTitle").val(ret.title);
    //         $("#editChoiceStem").val(ret.stem);
    //         $("#editChoiceAnswer").val(ret.answer);
    //         $("#editChoice").attr('readonly','readonly');
    //         $("#editChoice").modal('show');
    //     });
    // })



    //点击删除按钮的反应
    $('button.choiceDel').unbind();
    $('button.choiceDel').bind('click', function(e) {
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
                    $.post("/ink/delChoice/?room="+$("#roomId").val(), {'id': questionId},function (ret) {
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
    $("#choiceSave").click(function () {
        var options = new Array();//存储选项
        var checkbox = new Array();//存储选项对错
        var ans = new Array();//存储对的选项
        $("div.optionDiv").each(function () {
            checkbox.push($(this).children('span').children('input').prop('checked'));
            options.push($(this).children('input').val());
        });
        var optionNum = options.length;
        for(var i = options.length; i < 6; i ++)
        {
            options[i] = "";
            checkbox[i] = false;
        }
        for(var i = 0; i < 6; i ++)
        {
            //var text = $("<input type = \"text\" class = \"form-control\" name = \"" + String.fromCharCode(65+i) + "\" value = \"" + options[i] + "\">").appendTo($("#finalOptionDiv"));
            if(checkbox[i]){
                ans.push(i);
            }
        }
        var ansChar;
        if(ans.length==0){
            ansChar = "";
        }
        else{
            ansChar = String.fromCharCode(65+ans[0]);
            for(var i = 1; i < ans.length; i ++){
                ansChar = ansChar + " " + String.fromCharCode(65+ans[i]);
            }
        }

        //var answer = $("<input type = \"text\" class = \"form-control\" name = \"choiceAnswer\" value = \"" + ansChar + "\">").appendTo($("#finalOptionDiv"));
        var choiceTitle = $("#choiceTitle").val();
        var choiceStem = addChoiceEditor.getValue();
        //var choiceAnswer = $("#choiceAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });

        $.post('/ink/addChoice/?room='+$("#roomId").val(),
            {
                'choiceTitle': choiceTitle,
                'choiceStem': choiceStem,
                'A': options[0],
                'B': options[1],
                'C': options[2],
                'D': options[3],
                'E': options[4],
                'F': options[5],
                'optionNum': optionNum,
                'choiceAnswer': ansChar,
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('添加成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#choice input").each(function () {
                        this.val("");
                    })
                    $("#choice textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                    // initToastr();
                    // var $toast = toastr['error'](ret.message);
                }
            });
        })

    var editChoiceNum=0;

    //"编辑"按钮被点击时的响应
    $("button.choiceEdit").click(function() {
        $("div.simditor-toolbar").attr('style','top: 0px; width: 515px; left: 443px;');
        $("#editChoiceSave").attr('name',$(this).attr('name'));
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.ajax({
            type: "POST",
            url: "/ink/getChoiceById/?room="+$("#roomId").val(),
            data:{
                'choiceId': $(this).attr('name')
            },
            async:false,
            success: function (ret) {
                $("#editChoiceTitle").val(ret.title);
            editChoiceEditor.setValue(ret.stem);
            $("div.editOptionDiv").each(function () {
                $(this).remove();
            });
            var ans = new Array();
            for(var i = 0; i < ret.answer.length; i = i + 2){
                ans.push(ret.answer[i].charCodeAt()-65);
            }
            var option = [ret.optionA, ret.optionB, ret.optionC, ret.optionD, ret.optionE, ret.optionF];
            var check = [false, false, false, false, false, false];
            for(var i = 0; i < ans.length; i ++){
                check[ans[i]] = true;
            }
            for(var i = 0; i < 6; i ++){
                if(option[i] != ""){
                    editChoiceNum ++;
                    var div = $("<div class = \"input-group editOptionDiv\" id = \"editDiv" + i + "\"></div>").appendTo($("#editOptionsDiv"));
                var left = $("<span class = \"input-group-addon\"></span>").appendTo(div);
                if(check[i])
                    var checkbox = $("<input type = \"checkbox\" checked = \"true\">").appendTo(left);
                else
                    var checkbox = $("<input type = \"checkbox\">").appendTo(left);
                var text = $("<input type = \"text\" class = \"form-control\" value = \"" + option[i] + "\">").appendTo(div);
                var right = $("<span class = \"input-group-addon editDelButton\" id = \"" + i + "\">移除</span>").appendTo(div);
                }
            }
            $("#0").click(function () {
                editChoiceNum --;
                $("#editDiv0").remove();
            });
            $("#1").click(function () {
                editChoiceNum --;
                $("#editDiv1").remove();
            })
            $("#2").click(function () {
                editChoiceNum --;
                $("#editDiv2").remove();
            });
            $("#3").click(function () {
                editChoiceNum --;
                $("#editDiv3").remove();
            });
            $("#4").click(function () {
                editChoiceNum --;
                $("#editDiv4").remove();
            });
            $("#5").click(function () {
                editChoiceNum --;
                $("#editDiv5").remove();
            });
            $("#editChoice").modal('show');
            }
        });
    });

    //编辑选择题“添加选择题选项”按钮被点击时的反应
    $("#editOptionButton").click(function () {
        if(editChoiceNum > 5)
        {
            initToastr();
            var $toast = toastr['error']("最多设置六个选项");
        }
        else
        {
            editChoiceNum ++;
            var div = $("<div class = \"input-group editOptionDiv\"></div>").appendTo($("#editOptionsDiv"));
            var left = $("<span class = \"input-group-addon\"></span>").appendTo(div);
            if($("#editOptionCheckbox").prop('checked'))
                var checkbox = $("<input type = \"checkbox\" checked = \"true\">").appendTo(left);
            else
                var checkbox = $("<input type = \"checkbox\">").appendTo(left);
            var text = $("<input type = \"text\" class = \"form-control\" value = \"" + $("#editOptionText").val() + "\">").appendTo(div);
            var right = $("<span class = \"input-group-addon\">移除</span>").appendTo(div);

            //“移除”按钮被点击的反应
            right.click(function () {
                editChoiceNum --;
                div.remove();
            });
        }
    })

    //点击编辑模态框保存按钮的反应
    $("#editChoiceSave").click(function () {
        var options = new Array();//存储选项
        var checkbox = new Array();//存储选项对错
        var ans = new Array();//存储对的选项
        $("div.editOptionDiv").each(function () {
            checkbox.push($(this).children('span').children('input').prop('checked'));
            options.push($(this).children('input').val());
        });
        var optionNum = options.length;
        for (var i = options.length; i < 6; i++) {
            options[i] = "";
            checkbox[i] = false;
        }
        for (var i = 0; i < 6; i++) {
            // var text = $("<input type = \"text\" class = \"form-control\" name = \"" + String.fromCharCode(65 + i) + "\" value = \"" + options[i] + "\">").appendTo($("#editFinalOptionDiv"));
            if (checkbox[i]) {
                ans.push(i);
            }
        }
        var ansChar;
        if(ans.length == 0){
            ansChar = "";
        }
        else{
            ansChar = String.fromCharCode(65 + ans[0]);
            for (var i = 1; i < ans.length; i++) {
                ansChar = ansChar + " " + String.fromCharCode(65 + ans[i]);
            }
        }

        var choiceTitle = $("#editChoiceTitle").val();
        var choiceStem = editChoiceEditor.getValue();
        //var choiceAnswer = $("#choiceAnswer").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken")}
        });
        $.post('/ink/editChoice/?room='+$("#roomId").val(),
            {
                'choiceTitle': choiceTitle,
                'choiceStem': choiceStem,
                'A': options[0],
                'B': options[1],
                'C': options[2],
                'D': options[3],
                'E': options[4],
                'F': options[5],
                'optionNum': optionNum,
                'choiceAnswer': ansChar,
                'choiceId': $("#editChoiceSave").attr('name'),
            },
            function (ret) {
                if(ret.status == "success"){
                    initToastr();
                    var $toast = toastr['success']('编辑成功');
                    $("div.modal-backdrop").remove();
                    $("#rightPanel").html(ret.body);

                    //提交成功则清空模态框
                    $("#editChoice input").each(function () {
                        this.val("");
                    })
                    $("#editChoice textarea").each(function () {
                        this.val("");
                    })
                }
                else{
                    Confirm.show('提示', ret.message);
                }
            });
    })

})
