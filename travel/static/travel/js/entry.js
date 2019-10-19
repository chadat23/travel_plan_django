var gar_amber = 36;
var gar_red = 61;

function int0(x) {
    var parsed = parseInt(x);
    if (isNaN(parsed)) { return 0 }
    return parsed;
  }

function gar_math() {
    var i = 0;
    var j = 0;
    var grand_total = 0;
    
    while($("[name='supervision" + i.toString() + "']").length) {
        var supervision = $("[name='supervision" + i.toString() + "']").val();
        var planning = $("[name='planning" + i.toString() + "']").val();
        var contingency = $("[name='contingency" + i.toString() + "']").val();
        var comms = $("[name='comms" + i.toString() + "']").val();
        var teamselection = $("[name='teamselection" + i.toString() + "']").val();
        var fitness = $("[name='fitness" + i.toString() + "']").val();
        var env = $("[name='env" + i.toString() + "']").val();
        var complexity = $("[name='complexity" + i.toString() + "']").val();

        var total = int0(supervision) + int0(planning) + int0(contingency) + int0(comms) + int0(teamselection) + int0(fitness) + int0(env) + int0(complexity);
        if (total > 0) {
            $("[name='total" + i.toString() + "']").val(total);

            $("[name='total" + i.toString() + "']").removeClass('gar-green');
            $("[name='total" + i.toString() + "']").removeClass('gar-amber');
            $("[name='total" + i.toString() + "']").removeClass('gar-red');

            if (total < gar_amber) {$("[name='total" + i.toString() + "']").addClass('gar-green');}
            else if (total < gar_red) {$("[name='total" + i.toString() + "']").addClass('gar-amber');}
            else {$("[name='total" + i.toString() + "']").addClass('gar-red');}

            grand_total += total;
            j += 1;
        }        
        
        i += 1;
    }
    if (grand_total > 0) {
        avg = grand_total / j;

        $("[name='garaverage']").val(avg);

        $("[name='garaverage']").removeClass('gar-green');
        $("[name='garaverage']").removeClass('gar-amber');
        $("[name='garaverage']").removeClass('gar-red');

        if (avg < gar_amber) {$("[name='garaverage']").addClass('gar-green');}
        else if (avg < gar_red) {$("[name='garaverage']").addClass('gar-amber');}
        else {$("[name='garaverage']").addClass('gar-red');}
    }
};



$('[name^="supervision"]').blur(function() {
    gar_math();
    });

$('[name^="planning"]').blur(function() {
    gar_math();
    });

$('[name^="contingency"]').blur(function() {
    gar_math();
    });

$('[name^="comms"]').blur(function() {
    gar_math();
    });

$('[name^="teamselection"]').blur(function() {
    gar_math();
    });

$('[name^="fitness"]').blur(function() {
    gar_math();
    });

$('[name^="env"]').blur(function() {
    gar_math();
    });

$('[name^="complexity"]').blur(function() {
    gar_math();
    });

$('[name="garmitigated"]').blur(function() {
    $("[name='garmitigated']").removeClass('gar-green')
    $("[name='garmitigated']").removeClass('gar-amber')
    $("[name='garmitigated']").removeClass('gar-red')

    value = $("[name='garmitigated']").val()

    if (value < gar_amber) {$("[name='garmitigated']").addClass('gar-green')}
    else if (value < gar_red) {$("[name='garmitigated']").addClass('gar-amber')}
    else {$("[name='garmitigated']").addClass('gar-red')}
    });

function autofill_contact_info(index) {
    $.getJSON($SCRIPT_ROOT + '/traveler/get-responsible-party-info', {
        name: $('[name="contactname' + index + '"]').val()
    }, function(data) {
        $('[name="contactemail' + index + '"]').val(data.email);
        $('[name="contactwork' + index + '"]').val(data.work_number);
        $('[name="contacthome' + index + '"]').val(data.home_number);
        $('[name="contactcell' + index + '"]').val(data.cell_number);
    });
    return false;
    }

$('[name="contactname0"]').blur(function() {
    autofill_contact_info('0')
    });  


$('[name="contactname1"]').blur(function() {
    autofill_contact_info('1')
    });


$('[name="vehicleplate"]').blur(function() {
    console.log('starting')
    $.ajax({
        url: "/vehicles/ajax-get-vehicle-info-by-plate/",
        data: {'plate': $('[name="vehicleplate"]').val()},
        datatype: 'json',
        success: function (data) {
            console.log('going')
            console.log(data)
            $('[name="vehicleplate"]').val(data.plate);
            $('[name="vehiclemake"]').val(data.make);
            $('[name="vehiclemodel"]').val(data.model);
            $('[name="vehiclecolor"]').val(data.color);
        }

    })
    // $.getJSON($SCRIPT_ROOT + '/vehicle/get-vehicle-info', {
    //     plate: $('[name="vehicleplate"]').val()
    // }, function(data) {
    //     console.log('going')
    //     $('[name="vehicleplate"]').val(data.plate);
    //     $('[name="vehiclemake"]').val(data.make);
    //     $('[name="vehiclemodel"]').val(data.model);
    //     $('[name="vehiclecolor"]').val(data.color);
    // });
    return false;
    });

function autofill_travelerunit_info(index) {
    $.getJSON($SCRIPT_ROOT + '/travel/get-travelunit-info', {
        name: $('[name="travelername' + index + '"]').val()
    }, function(data) {
        $('[name="callsign' + index + '"]').val(data.call_sign);
        $('[name="packcolor' + index + '"]').val(data.pack_color);
        $('[name="tentcolor' + index + '"]').val(data.tent_color);
        $('[name="flycolor' + index + '"]').val(data.fly_color);
    });
    return false;
    }

$('[name="travelername0"]').blur(function() {
    autofill_travelerunit_info('0')
    });

$('[name="travelername1"]').blur(function() {
    autofill_travelerunit_info('1')
    });

$('[name="travelername2"]').blur(function() {
    autofill_travelerunit_info('2')
    });

$('[name="travelername3"]').blur(function() {
    autofill_travelerunit_info('3')
    });