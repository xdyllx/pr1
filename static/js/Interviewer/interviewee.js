/**
 * Created by chen on 2016/10/31.
 */

$(document).ready(function () {
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

})

function download(url, intervieweeId) {
    var form = $("<form>");   //定义一个form表单
    form.attr('style', 'display:none');   //在form表单中添加查询参数
    form.attr('target', '');
    form.attr('method', 'get');
    form.attr('action', url);

    var input1=$("<input>");
    input1.attr("type", "hidden");
    input1.attr("name", "intervieweeId");
    input1.attr("value", intervieweeId);

    form.append(input1);
    $('body').append(form);  //将表单放置在web中

    form.submit();
}