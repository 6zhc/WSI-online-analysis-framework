var toggle_boundary = function () {
    OSD_control.mask_controller = !OSD_control.mask_controller;
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
    size = (region_bound.DownRight_X - region_bound.UpLeft_X) / 980 * 2;
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = mouse_location.X - size, y = mouse_location.Y - size, width = size * 2, height = size * 2);
    var Bound_Rec_Viewport = viewer.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    var elt = document.createElement("div");
    elt.id = "point";
    console.log(typeof (OSD_control.grading))
    switch (Number(OSD_control.grading)) {
        case 1:
            color = "#8B0000";
            break;
        case 2:
            color = "#FF00FF";
            break;
        case 3:
            color = "#800080";
            break;
        case 4:
            color = "#4B0082";
            break;
        case 5:
            color = "#8A2BE2";
            break;
        case 6:
            color = "#0000FF";
            break;
        case 7:
            color = "#4169E1";
            break;
        case 8:
            color = "#4682B4";
            break;
        case 9:
            color = "#00FFFF";
            break;
        case 10:
            color = "#00FF00";
            break;
        case 11:
            color = "#008000";
            break;
        case 12:
            color = "#FFFF00";
            break;
        case 13:
            color = "#FFD700";
            break;
        case 14:
            color = "#FFA500";
            break;
        case 15:
            color = "#FF0000";
            break;
        case 16:
            color = "#000000";
            break;
        default:
            color = "#FFFFFF";
            break;
    }
    elt.style = "border-radius:50%;background-color:" + color + ";";
    viewer.addOverlay({
        element: elt,
        location: Bound_Rec_Viewport
    });
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
    $.post("/freehand_stomache_annotation/_record" + info_url, OSD_control.data_draw).done(function (data) {
        console.log(data);
        OSD_control.pt_false = '(';
        if (data.pt_false_x.length !== 0) {
            for (var i = 0; i < data.pt_false_x.length; i++) {
                OSD_control.pt_false = OSD_control.pt_false + '(' + parseInt(data.pt_false_x[i]) + ',' + parseInt(data.pt_false_y[i]) + ')' + ',';
            }
        }
        OSD_control.pt_false = OSD_control.pt_false + ')';
        update_mask();
        viewer.clearOverlays();
        if (data.branch_id >= 0 && flag_show_id) {
            showTips("您刚刚标注的是： " + data.branch_id, 50, 5);
            // setTimeout("alert(\"您刚刚标注的是： \" + data.branch_id );", 3000)
        }
        if (data.branch_id_find.length > 0) {
            showTips("您刚刚查找的标注是： " + data.branch_id_find, 50, 5);
            // setTimeout("alert(\"您刚刚标注的是： \" + data.branch_id );", 3000)
        }
    }).fail(function () {
        set_status(OSD_status2num.ready);
        // OSD_control.data_draw = {};
        // OSD_control.point_number = 0;
    });
    OSD_control.data_draw = {};
    OSD_control.point_number = 0;
};

var post_status = function () {
    console.log(OSD_control.check_box);
    set_status(OSD_status2num.data_processing);
    $.post("/freehand_stomache_annotation/_record_status" + info_url, OSD_control.check_box).done(function (data) {
        console.log(data);
        OSD_control.check_box = {"癌栓":false,
                           "出芽":false,
                           "神经丛浸润":false,
                           "周围小神经浸润":false,
                           "静脉浸润":false,
                           "淋巴管浸润":false};
    }).fail(function () {
        set_status(OSD_status2num.ready);
        OSD_control.data_draw = {"癌栓":false,
                           "出芽":false,
                           "神经丛浸润":false,
                           "周围小神经浸润":false,
                           "静脉浸润":false,
                           "淋巴管浸润":false};
    });
};

var get_status = function () {
    set_status(OSD_status2num.data_processing);
    $.post("/freehand_stomache_annotation/_get_status" + info_url, OSD_control.check_box).done(function (data) {
        console.log(data);
        OSD_control.check_box=data
        console.log("a",OSD_control.check_box)
        create_bool_controls()
    }).fail(function () {
        set_status(OSD_status2num.ready);
        OSD_control.check_box = {"癌栓":false,
                           "出芽":false,
                           "神经丛浸润":false,
                           "周围小神经浸润":false,
                           "静脉浸润":false,
                           "淋巴管浸润":false};
    });
};

function showTips(content, height, time) {
    //窗口的宽度
    var windowWidth = $(window).width();
    random = Math.random().toString()
    var tipsDiv = '<div class="tipsClass" id="tipsClass' + random + '">' + content + '</div>';

    $('body').append(tipsDiv);
    $('div.tipsClass').css({
        'top': height + 'px',
        'left': (windowWidth / 2) - 350 / 2 + 'px',
        'position': 'absolute',
        'padding': '3px 5px',
        'background': '#FF0000',
        'font-size': 12 + 'px',
        'margin': '0 auto',
        'text-align': 'center',
        'width': '100px',
        'height': 'auto',
        'color': '#fff',
        'opacity': '0.8'
    }).show();
    setTimeout("document.getElementById(\"tipsClass\"+" + random + ").remove();", (time * 1000));
}

var change_slide_id = function () {
    // console.log("Sending slide id and wait for return value");
    // set_status(OSD_status2num.data_processing);
    // console.log("Sending slide id and wait for return value");
    // $.getJSON(
    //     '/freehand_annotation/_change_slide_id'+info_url,
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
    var new_slide_id = Number($('#slide_id_select').select2('val')); //parseInt($('input[name="slide_id"]').val());
    if (available_slide.indexOf(new_slide_id) == -1) {
        alert("非法Slide ID!");
        return false;
    } else
        window.location.href = "/freehand_stomache_annotation?annotation_id=" + annotatorID
            + '&slide_id=' + new_slide_id.toString() + '&project=' + project;
    return false;
};

var update_slide_id = function () {
    // $.getJSON('/freehand_annotation/_get_slide_id' + info_url, {info: "nothing"}, function (data) {
        // Fetch data from '#slide_result' field and send as JSON
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


var getCheckboxValue = function (name) { //get which item is chosen
    var checkbox_tag = document.getElementsByName(name);
    var result={"癌栓":false,
            "出芽":false,
            "神经丛浸润":false,
            "周围小神经浸润":false,
            "静脉浸润":false,
            "淋巴管浸润":false}
    for (var i = 0; i < checkbox_tag.length; i++) {
        if (checkbox_tag[i].checked) {
            value=checkbox_tag[i].value;
            result[value]=true;
        }
    }
//     console.log(result)
    return result
    
};


var create_bool_controls = function() {
    var bool_box=["癌栓","出芽","神经丛浸润","周围小神经浸润","静脉浸润","淋巴管浸润"]
    
    var checked=OSD_control.check_box
    console.log("checked:",checked)
    for (var i = 0; i <= 5; i++) {
        var name=bool_box[i]
        var out_box=document.createElement("p")
        out_box.style.margin="10px 20px"
        var checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "checkbox";
        if (checked[name]=="false")
            checkbox.checked=false;
        else
            checkbox.checked=true;
        checkbox.value = name;
        checkbox.onchange = function () {
            OSD_control.check_box = getCheckboxValue("checkbox");
            post_status();
        };
        
        var text_box=document.createElement("span")
        var text = document.createTextNode(' ' + bool_box[i]+'\u00A0\u00A0');
        
        
        text_box.appendChild(text)
        out_box.appendChild(checkbox)
        
        out_box.appendChild(text_box)
        document.getElementById("bool").appendChild(out_box);
        
        if(i==5){
            var line=document.createElement("hr");
            document.getElementById("bool").appendChild(line);
        }
        document.getElementById(i.toString()).style.marginLeft = "10px";
    }
    document.getElementById("0").onchange();
}


var create_grading_controls = function () {
    // Generate grading controls
    var class_name=["0","粘膜固有层","粘膜肌层","粘膜下层","固有肌层","浆膜层","脂肪","pap","tub1","tub2","por1","por2","sig","muc","other","癌症区域","非癌症区域"]
    var color = ["#8B0000", "#FF00FF","#800080","#4B0082","#8A2BE2","#0000FF","#4169E1","#4682B4","#00FFFF","#00FF00","#008000","#FFFF00","#FFD700","#FFA500", "#FF0000", "#000000"]
    for (var i = -2; i <= 16; i++) {
        // if(i==0)
        //    continue;
        var out_box=document.createElement("p")
        out_box.style.margin="10px 20px"
        var radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "grading";
        radio.id = "" + i;
        radio.value = i;
        radio.onchange = function () {
            OSD_control.grading = getRadioValue("grading");
        };
        var style=document.createElement("canvas")
        style.width="15"
        style.height="15"
        //style.style.backgound-color="red"
        var s = style.getContext("2d")
        if (i==-1||i==0||i==-2)
            s.fillStyle = "white"
        else
            s.fillStyle = color[i-1]
        s.fillRect(0,0,15,15)
        
        var text_box=document.createElement("span")
        var text = document.createTextNode(' ' + class_name[i]+'\u00A0\u00A0');
        if (i == -1)
            text = document.createTextNode(' ' + "删除线" + '\u00A0\u00A0');
        else if (i == -2)
            text = document.createTextNode(' ' + "显示线id" + '\u00A0\u00A0');
        text_box.appendChild(text)
        out_box.appendChild(radio)
        out_box.appendChild(style)
        out_box.appendChild(text_box)
        document.getElementById("grading").appendChild(out_box);
        if(i==0||i==6||i==14||i==16){
            var line=document.createElement("hr");
            document.getElementById("grading").appendChild(line);
        }
        document.getElementById(i.toString()).style.marginLeft = "10px";
    }
    document.getElementById("-2").checked = true;
    document.getElementById("-2").onchange();
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
        $.getJSON('/freehand_stomache_annotation/record_viewing_pos' + info_url, data_to_send, function (data) {
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