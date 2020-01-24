const msg = (error, id) => {
  alertid = document.getElementById("alert");
  if (alertid) {
    alertid.parentNode.removeChild(alertid);
  }
  id.parentNode.innerHTML +=
    '<div id="alert" class="alert alert-danger alert-dismissible fade show" role="alert" style="margin-top:3px;">' +
    String(error) +
    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
    '<span aria-hidden="true">&times;</span>' +
    "</button>" +
    "</div>";
};

const removeAlert = () => {
  alertid = document.getElementById("alert");
  if (alertid) {
    alertid.parentNode.removeChild(alertid);
  }
};

const errorCheck = () => {
  alertid = document.getElementById("alert");
  console.log("error chcek");
  if (alertid) {
    msg("All fields should be validated");
    return false;
  } else {
    return true;
  }
};

const fnameValid = () => {
  const id = document.getElementById("fname");
  const fname = id.value;
  const num = /\d/;
  if (num.test(fname)) {
    msg("First Name should not contain a number", id);
  } else {
    removeAlert();
  }
};

const mnameValid = () => {
  const id = document.getElementById("mname");
  const mname = id.value;
  const num = /\d/;
  if (num.test(mname)) {
    msg("Middle Name should not contain a number", id);
  }
};

const lnameValid = () => {
  const id = document.getElementById("lname");
  const lname = id.value;
  const num = /\d/;
  if (num.test(lname)) {
    msg("Last Name should not contain a number", id);
  }
};

const emailValid = () => {
  const id = document.getElementById("email");
  const email = id.value;
  if (email.includes("@")) {
    if (email.includes(".")) {
      if (email.lastIndexOf(".") > email.lastIndexOf("@")) {
        removeAlert();
      } else {
        msg("Email should contain '.' dot after '@'.", id);
      }
    } else {
      msg("Email should contain '.' dot", id);
    }
  } else {
    msg("Email should contain '@'.", id);
  }
};

const emailCompare = () => {
  const email = document.getElementById("email").value;
  const id = document.getElementById("reemail");
  email2 = id.value;
  if (email.length === email2.length) {
    if (email === email2) {
      removeAlert();
    } else {
      msg("Email addresses should be equal.", id);
    }
  } else {
    msg("Email addresses should be equal.", id);
  }
};

const passValid = () => {
  console.log("pass");
  const id = document.getElementById("password");
  const pass = id.value;
  const num = /\d/;
  if (pass.length >= 8) {
    if (num.test(pass)) {
      removeAlert();
    } else {
      msg("Password should be AlphaNumeric.", id);
    }
  } else {
    msg("Password minimum limit is 8.", id);
  }
};

const passCompare = () => {
  const id = document.getElementById("repassword");
  const pass = document.getElementById("password").value;
  const pass2 = id.value;
  if (pass2.length === pass.length) {
    if (pass === pass2) {
      removeAlert();
    } else {
      msg("Password should be equal", id);
    }
  } else {
    msg("Password not equal.", id);
  }
};

const phoneValid = () => {
  const id = document.getElementById("phone");
  const phone = id.value;
  const pattern = /^[0-9]{10}$/;

  if (pattern.test(phone)) {
    removeAlert();
  } else {
    msg("Phone Number should be of 10 digits", id);
  }
};
