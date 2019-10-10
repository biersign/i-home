function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    $.get("/api/v1.0/areas", function(resp){
        if(resp.errno == "0"){
            var areas = resp.data;
            //使用js模板
            var html = template("areas_tmpl", {areas:areas});
            $("#area-id").html(html);
        }else{
            alert(resp.data);
        }
    });

    $("#form-house-info").submit(function(e){
        //阻止表单事件提交
        e.preventDefault();
        //提取表单中的数据
        data = {};
        $("#form-house-info").serializeArray().map(function(x){
            data[x.name] = x.value
        });
        //收集设施id信息
        facilities = []
        $(":checked[name=facility]").each(function(index, x){
            facilities[index] = $(x).val();
        });
        data.facilities = facilities;
        //向后端发送请求
        $.ajax({
            url: "/api/v1.0/houses/info",
            data: JSON.stringify(data),
            type: "post",
            contentType: "application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success:function(resp){
                if(resp.errno == "4101"){
                    location.href = "/login.html";
                } else if(resp.errno == "0"){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id);
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    });

    $("#form-house-image").submit(function(e){
        //阻止表单事件提交
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "/api/v1.0/houses/image",
            type:"post",
            dataType:"json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success:function(resp){
                if(resp.errno == "4101"){
                    location.href = "/login.html";
                } else if(resp.errno == "0"){
                   $(".house-image-cons").append('<img src="'+ resp.data.image_url +'">');
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })

})