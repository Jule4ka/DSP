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
      $('#data').DataTable({
        columns: [
          null,
          {searchable: false},
          {orderable: false, searchable: false},
          {orderable: false, searchable: false},
          null],
      });
    });

