window.onload = function () {
  let timeout;

  let password1 = document.getElementById("id_password1");
  let password2 = document.getElementById("id_password2");
  let error_weak_password = document.getElementById("error_weak_password");
  let error_different_passwords = document.getElementById(
    "error_different_passwords"
  );

  let strongPassword = new RegExp(
    "(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})"
  );

  function StrengthChecker(PasswordParameter) {
    if (strongPassword.test(PasswordParameter)) {
      error_weak_password.style.display = "none";
    } else {
      error_weak_password.style.display = "block";
      error_weak_password.style.color = "red";
    }
  }

  function checkPasswords() {
    if (password1.value != password2.value) {
      error_different_passwords.style.display = "block";
      error_different_passwords.style.color = "red";
    } else {
      error_different_passwords.style.display = "none";
    }
  }

  if (password1) {
    error_weak_password.style.display = "none";
    password1.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => StrengthChecker(password1.value), 500);
    });
  }

  if (password2) {
    error_different_passwords.style.display = "none";
    password2.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => checkPasswords(password2.value), 500);
    });
  }
};
