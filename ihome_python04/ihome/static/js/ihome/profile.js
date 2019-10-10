function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.ajax({
        url:"/api/v1.0/user/info",
        type:"GET",
        dataType:"json",
        success:function(resp){

           if(resp.errno == "0"){
                var image_url = resp.data.avatar_url;
                $("#user-avatar").attr("src", image_url);
                $("#user-name").val(resp.data.name);
           }else{
                alert(resp.errmsg);
           }
        }
    })




    $("#form-avatar").submit(function(e){
        //阻止表单行为
        e.preventDefault();
        //利用js自带的提交函数
        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            type:"post",
            dataType:"json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success:function(resp){
                if(resp.errno == "0"){
                    //保存成功
                    var avatarUrl = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatarUrl);
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    });

    $("#form-name").submit(function(e){
        //阻止表单请求
        e.preventDefault();
        var name = $("#user-name").val();
        //组织参数
        var req_data = {
            name: name
        };
        //转化为json模式
        var json_data = JSON.stringify(req_data);
        //发送ajax请求
        $.ajax({
            url: "/api/v1.0/users/name",
            data:json_data,
            contentType: "application/json",
            type:"PUT",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success: function(resp){
                if (resp.errno == "0"){
                     $(".error-msg").hide();
                     showSuccessMsg();
                     location.href = "/index.html";
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    })


})