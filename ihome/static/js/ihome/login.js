function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        // 向后端发送请求,提交用户的登陆信息
        var req_data = {
            mobile: mobile,
            password: passwd
        };

        // 将js对象转换为json字符串
        req_json = JSON.stringify(req_data);

        // 使用ajax发送请求
        $.ajax({
            url: "/api/v1_0/passport",  // 请求路径
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 0) {
                    location.href = "/";
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });
});