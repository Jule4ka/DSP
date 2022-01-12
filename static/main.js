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










var check = function() {
  if (document.getElementById('password').value ==
    document.getElementById('confirm_password').value) {
    document.getElementById('message').style.color = 'green';
    document.getElementById('message').innerHTML = 'matching';
  } else {
    document.getElementById('message').style.color = 'red';
    document.getElementById('message').innerHTML = 'not matching';
  }
}

