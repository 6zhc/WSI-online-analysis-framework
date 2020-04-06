$(document).ready(function () {
    $("#clinical_meta_data").click(function () {
        $("#patient_info").slideToggle("slow");
    });
});
$(document).ready(function () {
    $("#bio_meta_data").click(function () {
        $("#bio_info").slideToggle("slow");
    });
});
var demographic_update = function () {
    var data = JSON.stringify('demographic');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',
    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#demographic_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#demographic_info').append("<div id='property'><b>" + key + "</b>:  " + value + '</div>');
                $('#property').attr('id', key)
            })
            $('#ethnicity').mouseenter(function () {
                $('#ethnicity').append('<div class="ethnicity_inter" style="font-size:13px;color:red">(An individual\'s self-described social and cultural grouping, specifically whether an individual describes themselves as Hispanic or Latino. The provided values are based on the categories defined by the U.S. Office of Management and Business and used by the U.S. Census Bureau.)</div>')
            })
            $('#ethnicity').mouseleave(function () {
                $('.ethnicity_inter').css("display", "none");
            })
            $('#gender').mouseenter(function () {
                $('#gender').append('<div class="gender_inter" style="font-size:13px;color:red">(Male or Female.)</div>')
            })
            $('#gender').mouseleave(function () {
                $('.gender_inter').css("display", "none");
            })
            $('#days_to_birth').mouseenter(function () {
                $('#days_to_birth').append('<div class="days_to_birth_inter" style="font-size:13px;color:red">(Number of days between the date used for index and the date from a person\'s date of birth represented as a calculated negative number of days.)</div>')
            })
            $('#days_to_birth').mouseleave(function () {
                $('.days_to_birth_inter').css("display", "none");
            })
            $('#days_to_death').mouseenter(function () {
                $('#days_to_death').append('<div class="days_to_death_inter" style="font-size:13px;color:red">(Number of days between the date used for index and the date from a person\'s date of death represented as a calculated number of days.)</div>')
            })
            $('#days_to_death').mouseleave(function () {
                $('.days_to_death_inter').css("display", "none");
            })
            $('#vital_status').mouseenter(function () {
                $('#vital_status').append('<div class="vital_status_inter" style="font-size:13px;color:red">(The survival state of the person registered on the protocol.)</div>')
            })
            $('#vital_status').mouseleave(function () {
                $('.vital_status_inter').css("display", "none");
            })
        });

    event.preventDefault();
};
$(document).ready(function () {
    $("#demographic").click(function () {
        $("#demographic_info").slideToggle("slow");
        demographic_update();
    });
});

var diagnosis_update = function () {
    var data = JSON.stringify('diagnosis');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#diagnosis_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#diagnosis_info').append("<div id='property'><b>" + key + "</b>:  " + value + '</div>');
                $('#property').attr('id', key)
            })
            $('#tumor_grade').mouseenter(function () {
                $('#tumor_grade').append('<div class="tumor_grade_inter" style="font-size:13px;color:red">(Enumeration:G1,G2,G3,G4,GX,GB,High Grade,Low Grade,Unknown)</div>')
            })
            $('#tumor_grade').mouseleave(function () {
                $('.tumor_grade_inter').css("display", "none");
            })
        });

    event.preventDefault();

};
$(document).ready(function () {
    $("#diagnosis").click(function () {
        $("#diagnosis_info").slideToggle("slow");
        diagnosis_update();
    });
});

var exposure_update = function () {
    var data = JSON.stringify('exposure');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#exposure_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#exposure_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
            })
        });

    event.preventDefault();
};
$(document).ready(function () {
    $("#exposure").click(function () {
        $("#exposure_info").slideToggle("slow");
        exposure_update();
    });
});


var family_history_update = function () {
    var data = JSON.stringify('family_history');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            if (data == '{}') {
                $('#family_history_info').css("display:block");
            } else {
                result = JSON.parse(data);
                $('#family_history_info').empty();
                $.each(result, function (key, value) {
                    //alert(key,value);
                    //$('#successAlert').text(key+":"+value+'<br>').show();
                    $('#family_history_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
                })
            }
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#family_history").click(function () {
        $("#family_history_info").slideToggle("slow");
        family_history_update();
    });
});

var molecular_test_update = function () {
    var data = JSON.stringify('molecular_test');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            if (data == '{}') {
                $('#molecular_test_info').css("display:block");
            } else {
                result = JSON.parse(data);
                $('#molecular_test_info').empty();
                $.each(result, function (key, value) {
                    //alert(key,value);
                    //$('#successAlert').text(key+":"+value+'<br>').show();

                    $('#molecular_test_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
                })
            }
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#molecular_test").click(function () {
        $("#molecular_test_info").slideToggle("slow");
        molecular_test_update();
    });
});

var treatment_update = function () {
    var data = JSON.stringify('treatment');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            if (data == '{}') {
                $('#treatment_info').css("display:block");
            } else {
                result = JSON.parse(data);
                $('#treatment_info').empty();
                $.each(result, function (key, value) {
                    //alert(key,value);
                    //$('#successAlert').text(key+":"+value+'<br>').show();

                    $('#treatment_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
                })
            }
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#treatment").click(function () {
        $("#treatment_info").slideToggle("slow");
        treatment_update();
    });
});

var follow_up_update = function () {
    var data = JSON.stringify('follow_up');
    $.ajax({
        type: 'POST',
        url: '/get_patient_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            if (data == '{}') {
                $('#follow_up_info').css("display:block");
            } else {
                result = JSON.parse(data);
                $('#follow_up_info').empty();
                $.each(result, function (key, value) {
                    //alert(key,value);
                    //$('#successAlert').text(key+":"+value+'<br>').show();

                    $('#follow_up_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
                })
            }
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#follow_up").click(function () {
        $("#follow_up_info").slideToggle("slow");
        follow_up_update();
    });
});

var slide_update = function () {
    var data = JSON.stringify('slide');
    $.ajax({
        type: 'POST',
        url: '/get_bio_meta/',
        async: true,
        data: data,
        contentType: 'application/json'
    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#slide_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#slide_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
            })
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#slide").click(function () {
        $("#slide_info").slideToggle("slow");
        slide_update();
    });
});

var portion_update = function () {
    var data = JSON.stringify('portion');
    $.ajax({
        type: 'POST',
        url: '/get_bio_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#portion_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#portion_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
            })
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#portion").click(function () {
        $("#portion_info").slideToggle("slow");
        portion_update();
    });
});

var sample_update = function () {
    var data = JSON.stringify('sample');
    $.ajax({
        type: 'POST',
        url: '/get_bio_meta/',
        async: true,
        data: data,
        contentType: 'application/json',

    })
        .done(function (data) {
            result = JSON.parse(data);
            $('#sample_info').empty();
            $.each(result, function (key, value) {
                //alert(key,value);
                //$('#successAlert').text(key+":"+value+'<br>').show();

                $('#sample_info').append("<div><b>" + key + "</b>" + ":  " + value + '</div>');
            })
        });

    event.preventDefault();
}
$(document).ready(function () {
    $("#sample").click(function () {
        $("#sample_info").slideToggle("slow");
        sample_update();
    });
});

var slide_info_update = function () {
    demographic_update();
    diagnosis_update();
    exposure_update();
    family_history_update();
    follow_up_update();
    molecular_test_update();
    treatment_update();
    slide_update();
    sample_update();
    portion_update();
}

$(function () {
    $("#sr_update").click(function () {
        update_mag();
        return false;
    });
});

$(function () {
    $("#ss_update").click(function () {
        update_mag();
        return false;
    });
});

$(function () {
    $("#ds_update").click(function () {
        update_mag();
        return false;
    })
})

$(function () {
    $("#virtual-mag-usr-input").click(function () {
        update_mag(function (data) {
            var targzoom = parseFloat(document.getElementById("input-vmag").value);
            var currzoom = data.abs;
            viewer.viewport.zoomTo(targzoom / currzoom);
        });
    })
})