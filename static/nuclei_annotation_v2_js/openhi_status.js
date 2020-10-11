var interval = null;
var OSD_status = 0;
var OSD_status2num = {
    ready: 0,
    data_processing: 1,
    image_processing: 2,
    update_image: 3,
    saving_annotation: 4,
}
var sta_message = ["Ready", "Data Processing", "Image Processing", "Updating Image", "Saving Annotation"];

var blinker = function () {
    $('#status_block').fadeOut(150);
    $('#status_block').fadeIn(150);
    // This is the block -> █ <-
};

var set_status = function (sta) {
    switch (sta) {
        case 0:
            OSD_status = sta;
            clearInterval(interval);
            interval = null;
            break;
        case 4:
            OSD_status = sta;
            clearInterval(interval);
            interval = null;
            break;

        default:
            OSD_status = sta;
            // Set a flashing status bar during the processing/updating
            if (interval == null) {
                interval = setInterval(blinker, 300);
            }

    }
    $("#status_show").text(sta_message[sta]);
};