//function hrefBack() {
//    history.go(-1);
//}
//
//function decodeQuery(){
//    var search = decodeURI(document.location.search);
//    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
//        values = item.split('=');
//        result[values[0]] = values[1];
//        return result;
//    }, {});
//}
//
//$(document).ready(function(){
//    //获取房屋细节信息
//    var querydata = decodeQuery();
//    var house_id = querydata["id"];
//    alert(house_id);
//    $.get("/api/v1.0/house/"+ house_id, function(resp){
//        alert(resp.data.errmsg);
//        if("0" == resp.data.errno){
//            alert(resp.data.house_dict.img_urls);
//            alert(resp.data.house_dict.price);
//            alert(resp.data.house_dict);
//            $(".swiper-slide").html(template("image_urls", {images: resp.data.house_dict.img_urls, price: resp.data.house_dict.price}));
//            $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house_dict}));
//            // resp.user_id为访问页面用户,resp.data.user_id为房东
//            if (resp.data.user_id != resp.data.house_dict.user_id) {
//                $(".book-house").attr("href", "/booking.html?hid="+resp.data.house.hid);
//                $(".book-house").show();
//            }
//            var mySwiper = new Swiper ('.swiper-container', {
//                        loop: true,
//                        autoplay: 2000,
//                        autoplayDisableOnInteraction: false,
//                        pagination: '.swiper-pagination',
//                        paginationType: 'fraction'
//            });
//
//        }
//    });
//
//})

function hrefBack() {
    history.go(-1);
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // 获取该房屋的详细信息
    $.get("/api/v1.0/houses/" + houseId, function(resp){
        if ("0" == resp.errno) {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.data.house.img_urls, price:resp.data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house}));

            // resp.user_id为访问页面用户,resp.data.user_id为房东
            if (resp.data.user_id != resp.data.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid="+resp.data.house.hid);
                $(".book-house").show();
            }
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
        }
    })
})