$('.navTrigger').click(function () {
    $(this).toggleClass('active');
    $("#mainListDiv").toggleClass("show_list");
    $("#mainListDiv").fadeIn();
});

$('.nav div.main_list ul li a').click(function () {
    $('.navTrigger').toggleClass('active');
    $("#mainListDiv").toggleClass("show_list");
    $("#mainListDiv").fadeIn();
});


$(document).ready(function() {
    $('#data').DataTable( {
        "order": [[ 3, "desc" ]]
    } );
} );


