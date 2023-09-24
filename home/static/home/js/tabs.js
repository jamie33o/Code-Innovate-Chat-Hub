$(document).ready(function () {
    $('#tabs-nav a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
});