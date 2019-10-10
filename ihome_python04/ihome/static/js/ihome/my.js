function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success:function(resp){
            if(resp.errno == "0"){
                location.href = "/index.html"
            }
        }
    })
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
                $("#user-name").html(resp.data.name);
                $("#user-mobile").html(resp.data.mobile);
           }else{
                alert(resp.errmsg);
           }
        }
    })

})