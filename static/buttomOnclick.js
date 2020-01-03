let btn_click = function (clickType, slideID) {
    $.get('/' + clickType + '?slide_id=' + slideID, function (result) {
        if (result.time >= 0)
            setTimeout("location.reload();", result.time * 1000);
        alert(result.info);
    });
};

let btn_change_page = function (url, page_no) {
    if (page_no == -1)
        location.replace('/' + url + '?page_no=' + document.getElementById('page_no').value);
    else
        location.replace('/' + url + '?page_no=' + page_no);
};

let btn_predict = function () {
    SlideID = $('#slide_id_select').select2('val');
    Model = $('#model_select').select2('val');
    $.get('/make_pre_mask?slide_id=' + SlideID + '&model_name=' + Model, function (result) {
        if (result.time >= 0)
            setTimeout("location.reload();", result.time * 1000);
        alert(result.info);
    });
};