$(document).ready(function(){

    //校验是否实名认证
    $.get("/api/v1.0/user/auth", function(resp){
        if(resp.errno == "0"){
            if(!(resp.data.id_card && resp.data.real_name)){
                 $(".auth-warn").show();
                 return;
            }
             //获取当前用户的房源
            $.get("/api/v1.0/houses/user", function(resp){
                if(resp.errno ==  "0"){
                    //获取成功
                    alert(resp.data.house_dict);
                    $(".houses-list").html(template("house_list_tmpl", {houses:resp.data.house_dict}));
                }else{
                    $(".houses-list").html(template("house_list_tmpl", {houses:[]}));
                }
            });

        }else if(resp.errno == "4101"){
            //用户登陆
            location.href = "/login.html";
        }else{
           alert(0);
        }
    })


})