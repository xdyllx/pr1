$(document).ready(function() {
    var url = window.location.search;
    var loc = url.substring(url.lastIndexOf('=')+1,url.length);
    $("#roomId").val(loc);
    

    //点击选择题管理分页
    $("#choiceManage").click(function () {
        //$("#rightPanel").html('hello');
        $.ajax({url:'/ink/choiceManage/?room='+$("#roomId").val(), success:function (result){
            $("#rightPanel").html(result);
        }});
    });

    //点击填空题管理分页
    $("#completionManage").click(function () {
        $.ajax({url:'/ink/completionManage/?room='+$("#roomId").val(), success:function (result){
            $("#rightPanel").html(result);
        }});
    });
    //点击简答题管理分页
    $("#essayManage").click(function () {
        $.ajax({url:'/ink/essayManage/?room='+$("#roomId").val(), success:function (result){
            $("#rightPanel").html(result);
        }});
    });
    //点击编程题管理分页
    $("#codeManage").click(function () {
        $.ajax({url:'/ink/codeManage/?room='+$("#roomId").val(), success:function (result){
            $("#rightPanel").html(result);
        }});
    });

    //点击候选人管理分页
    $("#intervieweeManage").click(function () {
        $.ajax({url:'/ink/intervieweeManage/?room='+$("#roomId").val(), success:function (result){
            $("#rightPanel").html(result);
        }});
    });
    //点击进入房间按钮
    $("#enterRoom").click(function () {
        window.open("http://52.175.23.37:3000/interviewer?room="+$("#roomId").val());
    })
});

