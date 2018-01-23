function getCookie(name) {
    // 根据name提取对应的cookie值
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
    // $.get("/api/logout", function(data){
    //     if (0 == data.errno) {
    //         location.href = "/";
    //     }
    // })
    $.ajax({
        url: "/api/v1_0/session", // 请求路径
        type: "delete",  // 请求方式
        data: "hello",  //发送的请求体数据
        // contentType: "application/json",  // 指明向后端发送的是json格式的数据
        dataType: "json", // 指明从后端接收过来的是json数据
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == 0) {
                // 用户已登出
                location.href = "/"
                // $(".top-bar>.register-login").hide();
                // $(".top-bar>.user-info>.user-name").html(resp.user_name);
                // $(".top-bar>.user-info").show();

            } else {
                alert(resp.errmsg);
            }
        }
    })
}

$(document).ready(function(){
$.get("/api/v1_0/user", function(resp){
        // 用户未登录
        if (resp.errno == 4101) {
            location.href = "/login.html";
        }
        // 查询到了用户的信息
        else if (resp.errno == 0) {
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }

        }
    }, "json");
});