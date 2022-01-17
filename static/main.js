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
          {orderable: false, searchable: false},
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
$("#checkall").click(function () {
        if ($("#checkall").is(':checked')) {
            $("input[type=checkbox]").each(function () {
                $(this).prop("checked", true);
            });

        } else {
            $("input[type=checkbox]").each(function () {
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
