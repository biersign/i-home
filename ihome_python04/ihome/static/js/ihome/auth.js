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
            url:"/api/v1.0/user/auth",
            type:"get",
            dataType:"json",
            success:function(resp){
                if(resp.errno == "0"){
                    $("#real-name").val(resp.data.real_name);
                    $("#id-card").val(resp.data.id_card);
                }else{
                    alert(resp.errmsg)
                }
            }
        });

    $("#form-auth").submit(function(e){
        //组织表单提交
        e.preventDefault();
        var id_card = $("#id-card").val();
        var real_name = $("#real-name").val();

        var req_data = {
            "id_card": id_card,
            "real_name": real_name
        }
        var json_data = JSON.stringify(req_data);
        $.ajax({
            url:"/api/v1.0/user/auth",
            type:"post",
            data:json_data,
            contentType: "application/json",
            dataType:"json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success:function(resp){
                if(resp.errno == "0"){
                    alert(resp.errmsg);
                    location.href = "/index.html";
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })

})