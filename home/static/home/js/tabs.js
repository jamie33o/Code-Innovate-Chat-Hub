$(document).ready(function () {
    //for switching between tabs
    let prevTab;
    $('#tabs-nav a').on('click', function (e) {
        if (prevTab) {
            $(prevTab).removeClass('active');
        }
        e.preventDefault();
        $(this).tab('show');
        prevTab = this

    });
});