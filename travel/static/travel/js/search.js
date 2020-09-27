function getFilterValues () {
    var search = "";

    var tripleader = $("[name='tripleader']").val();
    var entrypoint = $("[name='entrypoint']").val();
    var startdate = $("[name='startdate']").val();
    var exitpoint = $("[name='exitpoint']").val();
    var enddate = $("[name='enddate']").val();
    var submitted = ''
    if (document.getElementById('submitted-yes').checked) {
        submitted = 'True'
    } else if (document.getElementById('submitted-no').checked) {
        submitted = 'False'
    }

    if( tripleader ) {
        search += 'tripleader=' + tripleader + '&';
    }

    if( entrypoint ) {
        search += 'entrypoint=' + entrypoint + '&';
    }
    
    if( startdate ) {
        search += 'startdate=' + startdate + '&';
    }
    
    if( exitpoint ) {
        search += 'exitpoint=' + exitpoint + '&';
    }
    
    if( enddate ) {
        search += 'enddate=' + enddate + '&';
    }

    if( submitted ) {
        search += 'submitted=' + submitted + '&';
    }

    return search
};

document.getElementById("applyfilter").onclick = function () { 
    search = getFilterValues()    

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById("clearfilter").onclick = function () {
    window.location.href = '/travel/search/'
};

document.getElementById('tripleaderascending').onclick = function () {
    search = getFilterValues() + 'tripleaderorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('tripleaderdescending').onclick = function () {
    search = getFilterValues() + 'tripleaderorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById('startdateascending').onclick = function () {
    search = getFilterValues() + 'startdateorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('startdatedescending').onclick = function () {
    search = getFilterValues() + 'startdateorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById('entrypointascending').onclick = function () {
    search = getFilterValues() + 'entrypointorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('entrypointdescending').onclick = function () {
    search = getFilterValues() + 'entrypointorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById('enddateascending').onclick = function () {
    search = getFilterValues() + 'enddateorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('enddatedescending').onclick = function () {
    search = getFilterValues() + 'enddateorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById('exitpointascending').onclick = function () {
    search = getFilterValues() + 'exitpointorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('exitpointdescending').onclick = function () {
    search = getFilterValues() + 'exitpointorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};

document.getElementById('submittedascending').onclick = function () {
    search = getFilterValues() + 'submittedorder=ascending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
document.getElementById('submitteddescending').onclick = function () {
    search = getFilterValues() + 'submittedorder=descending'

    if( search ) {
        window.location.href = "/travel/search/?" + search;
    }
};
