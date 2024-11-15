

function toggleNavbar() {
    let target = $('#navbarBasicExample');
    $('.navbar-burger').toggleClass('is-active');
    target.toggleClass('is-active');
}

window.addEventListener("scroll", function () {
    const navbar = document.querySelector(".navbar");
    if (window.scrollY > 50) { // Mengubah setelah scroll 50px
        navbar.classList.add("navbar-scroll");
    } else {
        navbar.classList.remove("navbar-scroll");
    }
});

window.addEventListener("scroll", function () {
    const buttonText = document.querySelector(".buttons .button.is-ghost");
    if (window.scrollY > 50) { // Setelah scroll 50px
        buttonText.classList.add("text-white-on-scroll");
    } else {
        buttonText.classList.remove("text-white-on-scroll");
    }
});


function signup() {
  let name = $("#name").val();
  let age = $("#age").val();
  let gender = $("#gender").val();
  let email = $("#email").val();
  let password = $("#password").val();

  if (name == '' || age == '' || gender == '' || email == '' || password == '') {
      Swal.fire(
          'Oops',
          'Data tidak lengkap!',
          'error'
      )
  } else {
    $.ajax({
        type: "POST",
        url: "/register/save",
        data: {
            name: name,
            age: age,
            gender: gender,
            email: email,
            password: password
        },
        success: function (response) {
            Swal.fire({
                title: 'Done',
                text: 'You are signed up, nice!',
                icon: 'success',
                showConfirmButton: false
            });
            
            setTimeout(function () {
                window.location.replace("/login");
            }, 1000); 
        }
    });
  }
}

function sign_in() {
  let email = $("#email").val();
  let password = $("#password").val();

  $.ajax({
    type: "POST",
    url: "/login_save",
    data: {
        email: email,
        password: password,
    },
    success: function (response) {
        if (response["result"] === "success") {
            $.cookie("mytoken", response["token"], { path: "/" });
            Swal.fire({
                icon: 'success',
                title: 'Signed in!',
                text: 'You are signed in, nice!',
                showConfirmButton: false
            })
            setTimeout (function () {
             window.location.replace(response["redirect_url"]);
            }, 1000);

        } else {
              // alert(response["msg"]);
              Swal.fire(
                  'Oops',
                  response["msg"],
                  'error'
              )
          }
      },
  });
}

function sign_out() {
    Swal.fire({
        title: 'Log out account?',
        text: "Anda yakin untuk keluar?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, log me out!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.removeCookie("mytoken", { path: "/" });
            Swal.fire({
                icon: 'success',
                title: 'Logged Out!',
                text: 'Berhasil keluar dari akun.',
                showConfirmButton: false
            })
            setTimeout(function () {
                window.location.replace("/login");
            }, 1000);
        }
    });
}


function openModal() {
  const modal = document.getElementById('modal');
  modal.classList.add('is-active');
}

function closeModal() {
  const modal = document.getElementById('modal');
  modal.classList.remove('is-active');
  modal.classList.add('is-closing');

  setTimeout(function () {
      modal.classList.remove('is-closing');
  }, 300);
}