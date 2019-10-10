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
        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
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

        //组织参数
        var req_data = {
            mobile: mobile,
            password: passwd
        };
        //参数转化为json模式
        var json_data = JSON.stringify(req_data);
        //发送ajax请求
        $.ajax({
            url: "/api/v1.0/session",
            type: "post",
            data: json_data,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function(resp){
                if(resp.errno == "0"){
                    //登陆成功， 跳转到首页
                    location.href = "/index.html"
                }else{
                    alert(resp.errmsg)
                }
            }
        })

    });
})