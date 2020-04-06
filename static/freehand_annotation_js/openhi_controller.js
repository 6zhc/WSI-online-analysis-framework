var toggle_boundary = function () {
    OSD_control.mask_controller = !OSD_control.mask_controller
    update_toggle_boundary_info();
    remove_mask();
    if (OSD_control.mask_controller) add_mask(TBA_control.reg_id);
};

var update_toggle_boundary_info = function () {
    if ($("#tog_result"))
        $("#tog_result").text("Boundary (on/off): " + (OSD_control.mask_controller ? "on" : "off"));
};

var recording_point = function () {
    OSD_control.data_draw['' + OSD_control.point_number] = {
        x: mouse_location.X,
        y: mouse_location.Y,
        grading: OSD_control.grading,
    };
    OSD_control.point_number = OSD_control.point_number + 1;
    //console.log(OSD_control.data_draw)
};

var mid_recording_point = function () {
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = mouse_location.X - 10, y = mouse_location.Y - 10, width = 20, height = 20);
    var Bound_Rec_Viewport = viewer.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    //console.log(mouse_location)
    var elt = document.createElement("div");
    elt.id = "point";
    elt.style = "border-radius:50%;background-color:red;";
    viewer.addOverlay({
        element: elt,
        location: Bound_Rec_Viewport
    });
};

var update_scale_bar = function () {
    //update_scale_bar_status = 1;
    if (OSD_control.scale_bar_controller) {
        var bar_length = region_bound.Width / 3 * image_info.um_per_px;
        var unit_length;
        var scale_bar_text = " ";
        if (bar_length < 1) {
            unit_length = bar_length;
            scale_bar_text = " " + unit_length + " um";
        } else if (bar_length <= 5) {
            unit_length = Math.floor(bar_length);
            bar_length = unit_length;
            scale_bar_text = " " + unit_length + " um";
        } else if (bar_length <= 20) {
            unit_length = Math.floor(bar_length / 5) * 5;
            bar_length = unit_length;
            scale_bar_text = " " + unit_length + " um";
        } else if (bar_length < 100) {
            unit_length = Math.floor(bar_length / 10) * 10;
            bar_length = unit_length;
            scale_bar_text = " " + unit_length + " um";
        } else if (bar_length < 1000) {
            unit_length = Math.floor(bar_length / 100);
            bar_length = unit_length * 100;
            scale_bar_text = " " + bar_length + " um";
        } else if (bar_length > 1000) {
            unit_length = Math.floor(bar_length / 1000);
            bar_length = unit_length * 1000;
            scale_bar_text = " " + unit_length + " mm";
        }
        if (document.getElementById("scale_bar")) {
            $("#scale_bar").text(scale_bar_text);
            document.getElementById("scale_bar").style.width = (bar_length
                / region_bound.Width / image_info.um_per_px
                * document.getElementById("openseadragon1").clientWidth
                - 1) + "px"
        }
    }
};

var post_record = function () {
    console.log(OSD_control.data_draw);
    set_status(OSD_status2num.data_processing);
    $.post("/_record", OSD_control.data_draw).done(function (data) {
        console.log(data);
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
        OSD_control.pt_false = '(';
        if (data.pt_false_x.length !== 0) {
            for (var i = 0; i < data.pt_false_x.length; i++) {
                OSD_control.pt_false = OSD_control.pt_false + '(' + parseInt(data.pt_false_x[i]) + ',' + parseInt(data.pt_false_y[i]) + ')' + ',';
            }
        }
        OSD_control.pt_false = OSD_control.pt_false + ')';
        update_mask();
    }).fail(function () {
        set_status(OSD_status2num.ready);
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
    });
};

var change_slide_id = function () {
    console.log("Sending slide id and wait for return value");
    set_status(OSD_status2num.data_processing);
    console.log("Sending slide id and wait for return value");
    $.getJSON(
        '/_change_slide_id',
        {id: $('input[name="slide_id"]').val(),},
        function (data) {
            console.log(data);
            if (data.status === 'slide id update successful') {
                location.reload();
                // remove_mask();
                // viewer.world.removeItem(viewer.world.getItemAt(0));
                // viewer.addTiledImage({
                //     tileSource: "/static/test.dzi",
                // });
            } else {
                $("#change_result_flash").empty();
                $("#change_result_flash").append(data.status)
            }
            update_slide_id();
        }
    );
    return false;
};

var update_slide_id = function () {
    $.getJSON('/_get_slide_id', {info: "nothing"}, function (data) {
        // Fetch data from '#slide_result' field and send as JSON
        $("#slide_result").text("Current slide: " + data.slide_id);
        document.getElementById("slide_id_input_box").setAttribute("value", data.slide_id);
    });
};

// For both ps_lv and grading ratio buttons.
var getRadioValue = function (name) { //get which item is chosen (name is radio name such as "PS_lv" and "grading")
    var radio_tag = document.getElementsByName(name);
    for (var i = 0; i < radio_tag.length; i++) {
        if (radio_tag[i].checked) {
            return radio_tag[i].value;
        }
    }
};

var create_grading_controls = function () {
    // Generate grading controls
    for (var i = 0; i <= Const_number.Max_grading; i++) {
        var radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "grading";
        radio.id = "" + i;
        radio.value = i;
        radio.onchange = function () {
            OSD_control.grading = getRadioValue("grading");
        };
        if (i <= 4) {
            var text = document.createTextNode(' ' + i + '\u00A0\u00A0');
        } else if (i == 5) {
            var text = document.createTextNode(' ' + 'Endothelial��Ƥϸ��[5]' + '\u00A0\u00A0')
        } else if (i == 6) {
            var text = document.createTextNode(' ' + 'Lymphocytes�ܰ�ϸ��[6]' + '\u00A0\u00A0')
        } else {
            var text = document.createTextNode(' ' + 'Unmark [0]' + '\u00A0\u00A0');
        }

        document.getElementById("grading").appendChild(radio);
        document.getElementById("grading").appendChild(text);
        document.getElementById(i.toString()).style.marginLeft = "10px";
    }

    //document.getElementsByName("PS_lv").style.marginRight = "10px";
    // document.getElementById("Z").checked=true;
    document.getElementById("0").checked = true;
};


var turn_low_mv = function () {
    console.log("Update image to LOW magnification view...");
    set_region_bound_centre({
        x: region_bound.Center_X,
        y: region_bound.Center_Y,
        width: TBA_control.low_mag_dim / image_info.um_per_px,
        height: TBA_control.low_mag_dim / image_info.um_per_px,
    });
};

var turn_high_mv = function () {
    console.log("Update image to High magnification view...");
    set_region_bound_centre({
        x: region_bound.Center_X,
        y: region_bound.Center_Y,
        width: TBA_control.high_mag_dim / image_info.um_per_px,
        height: TBA_control.high_mag_dim / image_info.um_per_px,
    });
};


var add_viewing_pos = function () {
    if (OSD_control.viewing_position_record_controller) {
        // Send request to remove current "reg_id"
        data_to_send = {
            upLeft_X: region_bound.UpLeft_X,
            upLeft_Y: region_bound.UpLeft_Y,
            downRight_X: region_bound.DownRight_X,
            downRight_Y: region_bound.DownRight_Y
        }
        $.getJSON('/record_viewing_pos', data_to_send, function (data) {
                if (parseInt(data.num_status) == 1) {
                    console.log(data.status);
                } else {
                    console.log("record viewing position has failed.");
                }
            }
        );
    }
};

var viewing_position_record = function () {
    OSD_control.viewing_position_record_controller = !OSD_control.viewing_position_record_controller;
    if ($("#Viewing_Position_result"))
        $("#Viewing_Position_result").text("Viewing Position Record: " + (OSD_control.viewing_position_record_controller ? "on" : "off"));
}