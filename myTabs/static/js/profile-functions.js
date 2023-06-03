var ex1 = document.getElementById("edit-profile-btn");
var ex2 = document.getElementById("edit-password-btn");

ex1.onclick = show_edit_profile;
ex2.onclick = show_edit_password;

function show_edit_profile() {
  document.getElementById("edit-profile").style.display = "block";
  document.getElementById("edit-password").style.display = "none";
}

function show_edit_password() {
  document.getElementById("edit-profile").style.display = "none";
  document.getElementById("edit-password").style.display = "block";
}
