function getCookie(name) {
    // 根据name提取对应的cookie值
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
//模态框居中的控制
function centerModals() {
    $('.modal').each(function (i) {   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top - 30);  //修正原先已经有的30个像素
    });
}

function setStartDate() {
    var startDate = $("#start-date-input").val();
    if (startDate) {
        $(".search-btn").attr("start-date", startDate);
        $("#start-date-btn").html(startDate);
        $("#end-date").datepicker("destroy");
        $("#end-date-btn").html("离开日期");
        $("#end-date-input").val("");
        $(".search-btn").attr("end-date", "");
        $("#end-date").datepicker({
            language: "zh-CN",
            keyboardNavigation: false,
            startDate: startDate,
            format: "yyyy-mm-dd"
        });
        $("#end-date").on("changeDate", function () {
            $("#end-date-input").val(
                $(this).datepicker("getFormattedDate")
            );
        });
        $(".end-date").show();
    }
    $("#start-date-modal").modal("hide");
}

function setEndDate() {
    var endDate = $("#end-date-input").val();
    if (endDate) {
        $(".search-btn").attr("end-date", endDate);
        $("#end-date-btn").html(endDate);
    }
    $("#end-date-modal").modal("hide");
}

function goToSearchPage(th) {
    var url = "/search.html?";
    url += ("aid=" + $(th).attr("area-id"));
    url += "&";
    var areaName = $(th).attr("area-name");
    if (undefined == areaName) areaName = "";
    url += ("aname=" + areaName);
    url += "&";
    url += ("sd=" + $(th).attr("start-date"));
    url += "&";
    url += ("ed=" + $(th).attr("end-date"));
    location.href = url;
}

$(document).ready(function () {
    $(".top-bar>.register-login").show();
    var mySwiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationClickable: true
    });
    $(".area-list a").click(function (e) {
        $("#area-btn").html($(this).html());
        $(".search-btn").attr("area-id", $(this).attr("area-id"));
        $(".search-btn").attr("area-name", $(this).html());
        $("#area-modal").modal("hide");
    });
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候
    $("#start-date").datepicker({
        language: "zh-CN",
        keyboardNavigation: false,
        startDate: "today",
        format: "yyyy-mm-dd"
    });
    $("#start-date").on("changeDate", function () {
        var date = $(this).datepicker("getFormattedDate");
        $("#start-date-input").val(date);
    });
    // $.post("/api/v1_0/session", function (resp) {
    //     if (resp.errno == 0){
    //         // 用户已登陆
    //         // location.herf = "/"
    //         $(".top-bar>.register-login").hide();
    //
    //     } else {
    //         alert(resp.errmsg);
    //     }
    // })

    $.ajax({
        url: "/api/v1_0/session", // 请求路径
        type: "post",  // 请求方式
        data: "hello",  //发送的请求体数据
        // contentType: "application/json",  // 指明向后端发送的是json格式的数据
        dataType: "json", // 指明从后端接收过来的是json数据
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == 0) {
                // 用户已登陆
                // location.herf = "/"
                $(".top-bar>.register-login").hide();
                $(".top-bar>.user-info>.user-name").html(resp.user_name);
                $(".top-bar>.user-info").show();

            } else {
                alert(resp.errmsg);
            }
        }
    })
});