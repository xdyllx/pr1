/**
 * Created by Liuyx on 2016/11/10.
 */

$(document).ready(function() {
    $("#registerButton").click(function () {
        $.ajaxSetup({
            headers: {"X-CSRFToken": getCookie("csrftoken")}
        });
        var name = $("#namesignup").val();
        var email = $("#emailsignup").val();
        var company = $("#companysignup").val();
        var password = $("#passwordsignup").val();
        var passwordConfirm = $("#passwordsignup_confirm").val();
        var input = $("#verificationInput").val();
        var pic = ($("#verificationImage").attr('src'));
        var index1 = pic.lastIndexOf('/')+1;
        var index2 = pic.lastIndexOf('.');
        var num = pic.substring(index1, index2);

        $.post("/ink/register/", {
            'name': name, 'email': email,
            'company': company, 'password': password, 'passwordConfirm': passwordConfirm,
            'verificationNum': num, 'verificationInput': input
        }, function (ret) {
            if (ret.status == 'success') {
                alert('Success!');
                location.href = '/ink/login/'
            }
            else {
               alert(ret.message);
            }

        });
    });

});

function deleteMessage() {
    $("#tips").remove();
}