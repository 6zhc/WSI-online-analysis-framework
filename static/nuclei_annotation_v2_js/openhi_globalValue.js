window.oncontextmenu = function (e) {
    e.preventDefault();
};

var Const_number = {
    Max_grading: 7,
    keyboard: ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
    Max_Slide_grading: 4,
    //MAX_ps_lv   : 2,
}

//the value used in openhi_controller.js
var OSD_control = {
    mask_id: 0,
    mask_controller: 1,
    ps_lv: 0,
    grading: 0,
    Slide_grading: 0,
    point_number: 0,
    data_draw: {},
    point_record_controller: 0,
    point_mid_record_controller: 0,
    pt_false: "()",
    scale_bar_controller: 1,
    viewing_position_record_controller: 0,
    point_controller: 1,
    points_annotation: 0,
};

var points = {
    point_x: [],
    point_y: [],
    grade: []
};

//the value update after OSD animation ans set by openhi_viewer.js
var region_bound = {
    UpLeft_X: 0,
    UpLeft_Y: 0,
    DownRight_X: 0,
    DownRight_Y: 0,
    Center_X: 0,
    Center_Y: 0,
    Width: 0,
    Height: 0,
};

//the value update after mouse move in OSD.
var mouse_location = {
    X: 0,
    Y: 0,
};

//the value update in openhi_controller
var image_info = {
    img_width: 0,  //MAX_X = data.img_width  - 1;
    img_height: 0,  //MAX_Y = data.img_height - 1;
    ps_lv: 0,  //MAX_PSLV
    um_per_px: 0.25,
    max_image_zoom: 0,  //I didn't use it, just come from back end.
    toggle_status: 0,
};

var TBA_control = {
    px_viewer_width: 0,//parseFloat(document.getElementById("openseadragon1").clientWidth),
    px_viewer_height: 0,//parseFloat(document.getElementById("openseadragon1").clientHeight),
    low_mag_dim: 580, // 512,      // micron
    high_mag_dim: 200, // 128,     // micron
    tba_status: 0,
    reg_id: 0,
    //micron_per_pixel : 0.25, // micron/pixel (from WSI metadata, valid only in TCGA-KIRC WSIs.)
};

var TBA_list = {
    // region_id : [x, y]
};



