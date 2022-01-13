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
          null,null,null,null,null,null,null,null,null,
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
          {orderable: false, searchable: false},
          null,null,null,null,null,
          {orderable: false, searchable: false}
        ],
    });
});

$(document).ready(function () {
      $('#my_assets').DataTable({
        columns: [
          null,null,null,null,null,
          {orderable: false, searchable: false}
        ],
    });
});

// function to check all on marketplace page for deletion
$(document).ready(function(){
$("#marketplace #checkall").click(function () {
        if ($("#marketplace #checkall").is(':checked')) {
            $("#marketplace input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("#marketplace input[type=checkbox]").each(function () {
                $(this).prop("checked", false);
            });
        }
    });

    $("[data-toggle=tooltip]").tooltip();
});

// function to check all on my-projects page for deletion
$(document).ready(function(){
$("#projects #checkall").click(function () {
        if ($("#projects #checkall").is(':checked')) {
            $("#projects input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("#projects input[type=checkbox]").each(function () {
                $(this).prop("checked", false);
            });
        }
    });

    $("[data-toggle=tooltip]").tooltip();
});





var check = function() {
  if (document.getElementById('password').value ==
    document.getElementById('confirm_password').value) {
    document.getElementById('message').style.color = 'green';
    document.getElementById('message').innerHTML = 'matching';
    document.getElementById('registerbutton').removeAttribute('disabled');
  } else {
    document.getElementById('message').style.color = 'red';
    document.getElementById('message').innerHTML = 'not matching';
    document.getElementById('registerbutton').setAttribute("disabled", "disabled");
  }
}
