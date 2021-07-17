var update_region_bound = function () {
    var bounds = viewer1.viewport.getBounds();
    region_bound.UpLeft_X = bounds.x * image_info.img_width;
    region_bound.UpLeft_Y = bounds.y * image_info.img_width;
    region_bound.Width = bounds.width * image_info.img_width;
    region_bound.Height = bounds.height * image_info.img_width;
    region_bound.DownRight_X = region_bound.UpLeft_X + region_bound.Width;
    region_bound.DownRight_Y = region_bound.UpLeft_Y + region_bound.Height;
    region_bound.Center_X = Math.round((region_bound.UpLeft_X + region_bound.DownRight_X) / 2);
    region_bound.Center_Y = Math.round((region_bound.UpLeft_Y + region_bound.DownRight_Y) / 2);
    console.log(region_bound)
};

var update_mouse_location = function (event) {
    var Point_position = viewer1.viewport.pointFromPixel(event.position);
    mouse_location.X = Math.round(Point_position.x * image_info.img_width);
    mouse_location.Y = Math.round(Point_position.y * image_info.img_width);
    if (OSD_control.point_record_controller) recording_point();
    if (OSD_control.point_mid_record_controller) mid_recording_point();
};

var update_image_info = function () {
    $.getJSON('get_info' + info_url, function (data) {  //get inform and create radio button,
        console.log(data);
        image_info = data;
        update_region_bound();
    });
};
