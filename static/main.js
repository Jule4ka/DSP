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


$(document).ready(function () {
      $('#marketplace').DataTable({
        columns: [
          null,null,null,null,null,null,
          {orderable: false, searchable: false}
        ],
    });
});

$(document).ready(function () {
      $('#assets').DataTable({
        columns: [
          null,null,null,null,null,null,null,null,null,null,
          {orderable: false, searchable: false}
        ],
    });
});

$(document).ready(function () {
      $('#projects').DataTable({
        columns: [
          null,null,null,null,null,
          {orderable: false, searchable: false}
        ],
    });
});


