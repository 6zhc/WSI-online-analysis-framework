var recording_point = function () {
    OSD_control.data_draw['' + OSD_control.point_number] = {
        x: mouse_location.X,
        y: mouse_location.Y,
        grading: OSD_control.grading,
    };
    size = (region_bound.DownRight_X - region_bound.UpLeft_X) / 980 * 2;
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = mouse_location.X - size, y = mouse_location.Y - size, width = size * 2, height = size * 2);
    var Bound_Rec_Viewport = viewer1.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    console.log(Bound_Rec_Viewport)
    var elt = document.createElement("div");
    elt.id = "point";

    switch (Number(OSD_control.grading)) {
        case 6:
            color = "#FFFFFF";
            break;
        case 7:
            color = "#000000";
            break;
        default:
            color = "#FFFFFF";
            break;
    }
    elt.style = "border-radius:50%;background-color:" + color + ";";
    viewer1.addOverlay({
        element: elt,
        location: Bound_Rec_Viewport
    });
    OSD_control.point_number = OSD_control.point_number + 1;
    // console.log(OSD_control.data_draw)
};

var mid_recording_point = function () {
    var Bound_Rec_Pixel = new OpenSeadragon.Rect(x = mouse_location.X - 10, y = mouse_location.Y - 10, width = 20, height = 20);
    var Bound_Rec_Viewport = viewer1.world.getItemAt(0).imageToViewportRectangle(Bound_Rec_Pixel);
    //console.log(mouse_location)
    var elt = document.createElement("div");
    elt.id = "point";
    elt.style = "border-radius:50%;background-color:red;";
    viewer1.addOverlay({
        element: elt,
        location: Bound_Rec_Viewport
    });
};


var post_record = function () {
    console.log(OSD_control.data_draw);
    switch (Number(OSD_control.grading)) {
        case 6:
            wipe();
            break;
        case 7:
            fill_blank();
            break;
        default:
            break;
    }
};


var wipe = function () {
    if (is_point) {
        return;
    }
    document.getElementById("warning2").innerText = "正在擦除";
    $.post("/re_annotation/_wipe" + info_url, OSD_control.data_draw).done(function () {
        // console.log(data);
        document.getElementById("warning2").innerText = "";
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
        OSD_control.pt_false = '()';
        update_image();
    }).fail(function () {
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
    });
};


var fill_blank = function () {
    if (is_point) {
        return;
    }
    document.getElementById("warning2").innerText = "正在填补";
    $.post("/re_annotation/_fill" + info_url, OSD_control.data_draw).done(function (data) {
        console.log(data);
        document.getElementById("warning2").innerText = "";
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
        OSD_control.pt_false = '()';
        update_image();
    }).fail(function () {
        OSD_control.data_draw = {};
        OSD_control.point_number = 0;
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

var create_corrector_controls = function () {
    // Generate corrector controls
    var class_name = ["橡皮擦", "填补笔"]
    var eng_name = ["eraser", "pen"]
    var color = ["#FFFFFF", "#000000"]

    for (var i = 0; i < 2; i++) {
        var out_box = document.createElement("p")
        out_box.style.margin = "10px 20px"
        var radio = document.createElement("input");
        radio.type = "radio"
        radio.name = "correcting";
        radio.id = "" + i;
        radio.value = i + 6;
        radio.onchange = function () {
            OSD_control.grading = getRadioValue("correcting");
        };
        var style = document.createElement("canvas")
        style.width = "15"
        style.height = "15"
        var s = style.getContext("2d")
        s.fillStyle = color[i]
        s.fillRect(0, 0, 15, 15)

        var text_box = document.createElement("span")
        var text = document.createTextNode(' ' + eng_name[i] + "(" + class_name[i] + ")" + '\u00A0\u00A0');

        text_box.appendChild(text)
        out_box.appendChild(radio)
        out_box.appendChild(style)
        out_box.appendChild(text_box)
        document.getElementById("corrector").appendChild(out_box);
        document.getElementById(i.toString()).style.marginLeft = "10px";
    }
    document.getElementById("0").checked = true;
    document.getElementById("0").onchange();
};


var create_grading_controls = function () {
    // Generate grading controls

    var class_name = ["删除细胞", "伯基特淋巴瘤细胞", "淋巴瘤细胞", "横纹肌肉瘤", "神经母细胞瘤细胞", "原幼淋巴细胞", "原粒细胞",
        "异常早幼粒细胞", "幼单核细胞", "原幼单核细胞", "幼巨核细胞", "原巨核细胞", "有核细胞", "不计入"];
    var eng_name = ["Remove cells",
        "Burkitt lymphoma",
        "Lymphoma cell",
        "Rhabdomyosarcoma",
        "Neuroblastoma cells",
        "Proto-juvenile lymphocytes",
        "The original granulocyte",
        "Abnormal promyelocytes",
        "Juvenile monocyte",
        "Prokaryotic mononuclear cells",
        "Young megakaryocyte progen",
        "Megakaryocyte",
        "Nucleated cells",
        "Not take into accountUndo",
        "Save and refresh"]
    var color = ['#FFFFFF', '#FF69B4', '#C71585', '#FF00FF', '#9400D3', '#6A5ACD', '#87CEFA', '#008B8B', '#008000',
        '#FFFF00', '#FF8C00', '#FF0000', '#00008B', '#000000'];
    for (var i = 0; i <= 13; i++) {
        var out_box = document.createElement("p");
        out_box.style.margin = "10px 20px";
        var radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "grading";
        radio.id = "type_" + i;
        radio.value = i;
        var style = document.createElement("canvas")
        style.width = "15";
        style.height = "15";
        var s = style.getContext("2d")
        s.fillStyle = color[i]
        s.fillRect(0, 0, 15, 15)

        var text_box = document.createElement("span")
        var text = document.createTextNode(' ' + eng_name[i] + "(" + class_name[i] + ")" + '\u00A0\u00A0');

        text_box.appendChild(text)
        out_box.appendChild(radio)
        out_box.appendChild(style)
        out_box.appendChild(text_box)
        document.getElementById("marker").appendChild(out_box);
        document.getElementById("type_" + i.toString()).style.marginLeft = "10px";
    }
    document.getElementById("type_0").checked = true;
};