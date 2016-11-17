$(document).ready(function() {
    //点击房间管理分页
    $("#roomManage").click(function () {
        $.ajax({url:'ink/roomManage', success:function (result){
            $("#rightPanel").html(result);
        }});
    });

    //点击候选人管理分页
    $("#candidateManage").click(function () {
        $.ajax({url:'ink/candidateManage', success:function (result){
            $("#rightPanel").html(result);
        }});
    });
});

function logoutConfirm() {
    Confirm.show('', '确定要退出登录吗?', {'Delete': {
        'primary': true,
        'callback': function () {
            $.ajaxSetup({
            headers: {"X-CSRFToken": getCookie("csrftoken")}
            });
            $.post("/ink/logout/",{}, function (ret) {
                if (ret.status == 'success') {
                    location.href = '/ink/login/'
                }
            });
        }
    }
    })
}