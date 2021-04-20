var update_region_bound = function () {
    var bounds = viewer.viewport.getBounds();
    region_bound.UpLeft_X = bounds.x * image_info.img_width;
    region_bound.UpLeft_Y = bounds.y * image_info.img_width;
    region_bound.Width = bounds.width * image_info.img_width;
    region_bound.Height = bounds.height * image_info.img_width;
    region_bound.DownRight_X = region_bound.UpLeft_X + region_bound.Width;
    region_bound.DownRight_Y = region_bound.UpLeft_Y + region_bound.Height;
    region_bound.Center_X = Math.round((region_bound.UpLeft_X + region_bound.DownRight_X) / 2);
    region_bound.Center_Y = Math.round((region_bound.UpLeft_Y + region_bound.DownRight_Y) / 2);
    //console.log(region_bound)
};

var update_mouse_location = function (event) {
    var Point_position = viewer.viewport.pointFromPixel(event.position);
    mouse_location.X = Math.round(Point_position.x * image_info.img_width);
    mouse_location.Y = Math.round(Point_position.y * image_info.img_width);
    if (OSD_control.point_record_controller) recording_point();
    if (OSD_control.point_mid_record_controller) mid_recording_point();
};

var update_image_info = function () {
    $.getJSON('/nuclei_annotation_v2/_get_info' + info_url, {}, function (data) {  //get inform and create radio button,
        // Print received data from the back-end
        console.log(data);
        image_info = data;
        // create_PSLV_controls();
        create_grading_controls();
        document.querySelector("#svs_pro").textContent = JSON.stringify(data.properties, null, ' ');
        // document.getElementById("7").onchange();
        // create_slide_grading_controls();
        update_toggle_boundary_info();
        update_region_bound();
    });
};

var set_region_bound_centre = function (rec) {
    //x : centre_x
    //y : centre_y
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = rec.x - rec.width / 2, y = rec.y - rec.height / 2, width = rec.width, height = rec.height);
    var Bound_Rec_Viewport = viewer.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    viewer.viewport.fitBoundsWithConstraints(Bound_Rec_Viewport);
};

var set_region_bound = function (rec) {
    //x : left_x
    //y : up_y
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = rec.x, y = rec.y, width = rec.width, height = rec.height);
    var Bound_Rec_Viewport = viewer.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    viewer.viewport.fitBoundsWithConstraints(Bound_Rec_Viewport);
};

var add_mask = function (region_id) {
    region_coor = TBA_list[String(region_id)];
    OSD_control.mask_id = OSD_control.mask_id + 1;
    var local_mask_id = OSD_control.mask_id;
    var data_askFor = { //asking image is larger than we see
        var1: region_coor[0] - 256,    // buffer is the extra edge of the image that we load
        var2: region_coor[1] - 256,
        var3: region_coor[0] + 255,
        var4: region_coor[1] + 255,
        var5: 512,
        var6: 512,
        var7: region_id,
    };
    console.log(data_askFor);
    set_status(OSD_status2num.image_processing);
    $.getJSON('/nuclei_annotation_v2/_update_image' + info_url, data_askFor, //asking for the new image
        function (data) {
            console.log(data);
            while (viewer.world.getItemCount() >= 20)
                viewer.world.removeItem(viewer.world.getItemAt(1));
            set_status(OSD_status2num.update_image);
            var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = data_askFor.var1, y = data_askFor.var2,
                width = data_askFor.var3 - data_askFor.var1 + 1, height = data_askFor.var4 - data_askFor.var2 + 1);
            var Bound_Rec_Viewport = viewer.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
            // viewer.tileSources.url = data.slide_url;
            viewer.addTiledImage({
                tileSource: {
                    type: 'image',
                    url: data.background_url,
                },
                x: Bound_Rec_Viewport.x,
                y: Bound_Rec_Viewport.y,
                width: Bound_Rec_Viewport.width,
                success: function () {
                    while (viewer.world.getItemCount() > 2)
                        viewer.world.removeItem(viewer.world.getItemAt(1));
                    viewer.addTiledImage({
                        tileSource: {
                            type: 'image',
                            url: data.mask_url,
                        },
                        x: Bound_Rec_Viewport.x,
                        y: Bound_Rec_Viewport.y,
                        width: Bound_Rec_Viewport.width,
                        // opacity: 0.5,
                        success: function () {
                            set_status(OSD_status2num.ready);
                            if (!OSD_control.mask_controller) remove_mask();
                            add_region_label();
                        },
                        false: function () {
                        }
                    });
                    set_status(OSD_status2num.ready);
                    if (!OSD_control.mask_controller) remove_mask();
                },
                false: function () {
                }
            });

        });
};

var update_mask = function (region_id) {
    remove_mask();
    add_mask(region_id)
};

var remove_mask = function () {
    while (viewer.world.getItemCount() >= 2)
        viewer.world.removeItem(viewer.world.getItemAt(1));
};

var OSD_open_function = function () {
    setTimeout(function () {
        update_region_bound();
        update_scale_bar();
        update_tb_list();
    }, 300)
};

var animation_start_function = function () {
    update_region_bound();
    update_scale_bar();
}

var animation_function = function () {
    update_region_bound();
    //add_viewing_pos();
    update_scale_bar();
    if (Math.round(region_bound.Width) == Math.round(TBA_control.high_mag_dim / image_info.um_per_px)) {
        viewer.navigator.element.parentElement.parentElement.style.display = 'none';
        document.getElementById("scale_bar").style.display = 'none';
        ;
    } else {
        viewer.navigator.element.parentElement.parentElement.style.display = 'block';
        document.getElementById("scale_bar").style.display = 'block';
    }
};

var animation_finsh_function = function () {
    update_region_bound();
    add_viewing_pos();
    update_scale_bar();
    if (document.getElementById("tb_warn"))
        document.getElementById("tb_warn").innerHTML = "";
    if (Math.round(region_bound.Width) == Math.round(TBA_control.high_mag_dim / image_info.um_per_px)) {
        viewer.navigator.element.parentElement.parentElement.style.display = 'none';
    } else
        viewer.navigator.element.parentElement.parentElement.style.display = 'block';
};

var OSD_fullpage_function = function (e) {
    if (!e.fullpage) {
        console.log(region_bound)
    }
    //Do the follow after finish full page action.
    // I have no idea how to do it,then I just set timeout.
    setTimeout(function () {
        update_region_bound();
    }, 200);
};
