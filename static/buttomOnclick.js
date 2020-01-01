let btn_click = function (clickType, slideID) {
    $.get('/' + clickType + '?slide_id=' + slideID, function (result) {
        setTimeout("location.reload();", result.time * 1000);
        alert(result.info);
    });
};