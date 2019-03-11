// 设置cookie
function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  var expires = "expires=" + d.toGMTString();
  document.cookie = cname + "=" + cvalue + "; " + expires;
}

// 获取指定cookie 的值
function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i].trim();
    if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
  }
  return "";
}

// 删除cookie
function delCookie(key) {
  var date = new Date();
  date.setTime(date.getTime() - 1);
  var delValue = getCookie(key);
  if (!!delValue) {
    document.cookie = key + '=' + delValue + ';expires=' + date.toGMTString();
  }
}

// 检查cookie是否设置
function checkCookie() {
  var user_token = getCookie("user_token");
  if (user_token == "") {
    window.location.href = "/login.html";
  }
}

//  账号登出
function userLogout() {
  delCookie("user_id");
  delCookie("username");
  delCookie("user_alias");
  delCookie("user_token");
  window.location.href = "/login.html";
}

// show alert
function showAlert(text, level="alert-danger") {
  $('.alert').removeClass("d-none");
  // $('.alert').removeClass("alert-danger");
  $('.alert').addClass(level);
  $("#alert-text").text(text);
}

