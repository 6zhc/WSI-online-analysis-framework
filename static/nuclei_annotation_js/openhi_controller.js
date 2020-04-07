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
    if (TBA_control.tba_status == 0) return;
    OSD_control.data_draw['' + OSD_control.point_number] = {
        x: mouse_location.X - TBA_list[String(TBA_control.reg_id)][0] + 256,
        y: mouse_location.Y - TBA_list[String(TBA_control.reg_id)][1] + 256,
        grading: OSD_control.grading,
        region_id: TBA_control.reg_id
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
    if (TBA_control.tba_status === 0) return;
    console.log(OSD_control.data_draw);
    set_status(OSD_status2num.data_processing);
    $.post("/nuclei_annotation/_record" + info_url, OSD_control.data_draw).done(function (data) {
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
        add_mask(data.region_id);
    }).fail(function () {
        set_status(OSD_status2num.ready);
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
    });
};

var change_slide_id = function () {
    // console.log("Sending slide id and wait for return value");
    // set_status(OSD_status2num.data_processing);
    // console.log("Sending slide id and wait for return value");
    // $.getJSON(
    //     '/_change_slide_id',
    //     {id: $('input[name="slide_id"]').val(),},
    //     function (data) {
    //         console.log(data);
    //         if (data.status === 'slide id update successful') {
    //             location.reload();
    //             // remove_mask();
    //             // viewer.world.removeItem(viewer.world.getItemAt(0));
    //             // viewer.addTiledImage({
    //             //     tileSource: "/static/test.dzi",
    //             // });
    //         } else {
    //             $("#change_result_flash").empty();
    //             $("#change_result_flash").append(data.status)
    //         }
    //         update_slide_id();
    //     }
    // );
    var new_slide_id = parseInt($('input[name="slide_id"]').val())
    if (available_slide.indexOf(new_slide_id) == -1) {
        alert("非法Slide ID!");
        return false;
    } else
        window.location.href("/nuclei_annotation?annotation_id=" + annotatorID
            + '&slide_id=' + new_slide_id.toString());
    return false;
};

var update_slide_id = function () {
    // $.getJSON('/_get_slide_id', {info: "nothing"}, function (data) {
    //     // Fetch data from '#slide_result' field and send as JSON
    $("#slide_result").text("Current slide: " + slideID);
    document.getElementById("slide_id_input_box").setAttribute("value", slideID);
    // });
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

var create_PSLV_controls = function () {
    // Generate PSLV controls
    for (var i = 0; i <= image_info.ps_lv; i++) {
        var radio = document.createElement("input"); //syntax
        radio.type = "radio";
        radio.name = "PS_lv";
        radio.id = "" + Const_number.keyboard[i];
        radio.value = i;
        radio.onchange = function () {
            OSD_control.ps_lv = getRadioValue("PS_lv");   // Update the PSLV value
            update_mask()    // Perform standard update image routine
        }; // function is below
        var text = document.createTextNode(' ' + Const_number.keyboard[i] + ' : ' + i + '\u00A0\u00A0');
        document.getElementById("PS_lv").appendChild(radio);
        document.getElementById("PS_lv").appendChild(text);
        document.getElementById(Const_number.keyboard[i]).style.marginLeft = "5px";
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

var create_slide_grading_controls = function () {
    // Generate grading controls
    for (var i = 0; i <= Const_number.Max_Slide_grading; i++) {
        var radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "Slide_grading";
        radio.id = "s" + i;
        radio.value = i;
        radio.onchange = function () {
            OSD_control.Slide_grading = getRadioValue("Slide_grading");
            submit_check_box();
        };
        var text = document.createTextNode(' ' + i + '\u00A0\u00A0');

        document.getElementById("Slide_grading").appendChild(radio);
        document.getElementById("Slide_grading").appendChild(text);
        document.getElementById(i.toString()).style.marginLeft = "10px";
    }

    check_box_text = ""

    $.getJSON('/read_final_result' + info_url, {}, function (data) {
        // Fetch data from '#slide_result' field and send as JSON
        data.result.toString().trim().split('\n').forEach(function (v, i) {
            if (i == 0) {
                document.getElementById('s' + v[15]).checked = true;
                OSD_control.Slide_grading = parseInt(v[15])
            } else {
                check_box_text = '<input type="checkbox" onclick="submit_check_box()" name="dockor_checkbox" id = "r' + i.toString() +
                    '" value="' + v.slice(3) + '"/> ' + v.slice(3) + ' <br/>'
                //console.log(check_box_text)
                var temp = document.createElement("span");
                temp.innerHTML = check_box_text
                document.getElementById("check_box").appendChild(temp);
                if (v[1] == 'X')
                    document.getElementById('r' + i.toString()).checked = true;
            }
        })
        console.log(data)
    });

    // check_box_text = '<input type="checkbox" name="dockor_checkbox" value="Ha, Ha"/> Ha, Ha <br/>'+
    //     '<input type="checkbox" name="dockor_checkbox" value="Hei, Hei"/> Hei, Hei<br/>'+
    //     '<a href=# id=submit_check_box><button class="btn btn-default">save</button></a>';


    // document.getElementsByName("PS_lv").style.marginRight = "10px";
    // document.getElementById("Z").checked=true;
};

var submit_check_box = function () {
    obj = document.getElementsByName("dockor_checkbox");
    final_report = "Slide_grading: " + OSD_control.Slide_grading + "\n";
    for (var k = 0; k < obj.length; k++) {
        final_report += '['
        if (obj[k].checked)
            final_report += 'X]';
        else
            final_report += ' ]';
        final_report += obj[k].value;
        final_report += '\n'
    }
    $.getJSON('/save_final_result' + info_url, {final_result: final_report}, function (data) {
        // Fetch data from '#slide_result' field and send as JSON
        console.log(data)
    });
}
/*
var update_TBA_control = function () {
    TBA_control.px_viewer_width  = parseFloat(document.getElementById("openseadragon1").clientWidth);
    TBA_control.px_viewer_height = parseFloat(document.getElementById("openseadragon1").clientHeight);
};
*/

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

var add_TBA_list = function () {
    console.log("Add current region (sub-window) to the TBA list.");
    if (Math.round(region_bound.Width) == Math.round(TBA_control.low_mag_dim / image_info.um_per_px)) {
        // Send the coordinate to the system
        $.getJSON('/nuclei_annotation/_add_sw' + info_url, {x: region_bound.Center_X, y: region_bound.Center_Y},
            function (data) {
                if (parseInt(data.num_status) == 1) {
                    console.log(data.status);
                    update_tb_list(true);
                } else {
                    console.log("Adding sub-window has failed.")
                }
            }
        );
    } else {
        document.getElementById("tb_warn").innerHTML = "Cannot add: Click 'Magnification: Low' first.";
    }
};

var remove_TBA_list = function () {
    console.log("Remove current region (sub-window) from the TBA list.");
    if (TBA_control.tba_status) {
        // Send request to remove current "reg_id"
        $.getJSON('/nuclei_annotation/_rm_sw' + info_url, {sw_id: TBA_control.reg_id}, function (data) {
                if (parseInt(data.num_status) == 1) {
                    console.log(data.status);
                    update_tb_list();
                } else {
                    console.log("Removing sub-window has failed.");
                }
            }
        );
        TBA_control.tba_status = 0;
        remove_mask();
    } else {
        document.getElementById("tb_warn").innerHTML = "Cannot remove: Select the 'Region X' first.";
    }
};

function makeUL(array) {
    // Create the list element:
    var list = document.createElement('ol');
    list.setAttribute("id", "tba_ul_list");

    for (var i = 0; i < array.length; i++) {
        // Create the list item:
        var item = document.createElement('li');
        item.setAttribute("class", "clicky");
        item.setAttribute("id", "regid_" + array[i].substring(7, array[i].length));
        item.setAttribute("onClick", "change_region(this.id)");

        // Set its contents:
        item.appendChild(document.createTextNode(array[i]));

        // Add it to the list:
        list.appendChild(item);
    }
    // Finally, return the constructed list:
    return list;
}

var update_tb_list = function (add_last_mask = false) {
    // Update the TBA list
    // Fetch TBA list information and update on the web page.
    $.getJSON('/nuclei_annotation/_update_tb_list' + info_url, {}, function (data) {
        var max_region = parseInt(data.max_region);
        var reg_list = [];      // Clear the list.
        TBA_list = {};
        for (var i = 0; i < max_region; i++) {
            reg_list.push('Region ' + String(data.reg_list[i][0]));
            TBA_list[String(data.reg_list[i][0])] = [data.reg_list[i][1], data.reg_list[i][2]]
        }
        document.getElementById('tb_list').innerHTML = "";
        document.getElementById('tb_list').appendChild(makeUL(reg_list));
        if (add_last_mask) {
            change_region("regid_" + data.reg_list[max_region - 1][0]);
        }
    });
};

function change_region(region_str) {
    if (region_str != 'reg_selected') {
        if (TBA_control.tba_status && document.getElementById("reg_selected")) {
            document.getElementById("reg_selected").id = "regid_" + String(TBA_control.reg_id);
            TBA_control.tba_status = 0;
        }
        TBA_control.reg_id = parseInt(region_str.substring(6, region_str.length));  // Fetch the region id from the <li> string
        document.getElementById("regid_" + String(TBA_control.reg_id)).id = "reg_selected"; // Highlight the region id in the list
        console.log("Update image to LOW magnification view...");
        set_region_bound_centre({
            x: TBA_list[String(TBA_control.reg_id)][0],
            y: TBA_list[String(TBA_control.reg_id)][1],
            width: TBA_control.low_mag_dim / image_info.um_per_px,
            height: TBA_control.low_mag_dim / image_info.um_per_px,
        });
        if (OSD_control.mask_controller)
            add_mask(TBA_control.reg_id);
        TBA_control.tba_status = 2;
    } else {
        set_region_bound_centre({
            x: TBA_list[String(TBA_control.reg_id)][0],
            y: TBA_list[String(TBA_control.reg_id)][1],
            width: TBA_control.low_mag_dim / image_info.um_per_px,
            height: TBA_control.low_mag_dim / image_info.um_per_px,
        });
        add_mask(TBA_control.reg_id);
    }
}

var check_TBA_region = function () {
    if (TBA_control.tba_status == 1) {
        if (TBA_list[String(TBA_control.reg_id)][0] != Math.round(region_bound.Center_X)
            && TBA_list[String(TBA_control.reg_id)][1] != Math.round(region_bound.Center_Y)) {
            TBA_control.tba_status = 0;
            if (document.getElementById("reg_selected"))
                document.getElementById("reg_selected").id = "regid_" + String(TBA_control.reg_id);
        }
    }
}

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