/**
 * Created by dimones-dev on 02.09.16.
 */
$(document).ready(function () {
    if(Cookies.get('device_id') == null || Cookies.get('device_id') == undefined)
        Cookies.set('device_id',guid());
});

function auth(){
    var device_id = Cookies.get('device_id');
    var jqxhr = $.post("/admin/auth", { "username" : $("#input_username").val(),
                                                        "password" : $("#input_password").val(),
                                                        "device_id": device_id })
      .done(function(data) {
//        alert(data);
        var ret = JSON.parse(data);
          console.log(ret);
        if(ret["succeed"] == true)
        {
            Cookies.set('device_token',ret["device_token"]);
            Cookies.set('isAuthed',true);
            console.log('Успешная авторизация');
            window.location= location.protocol + "//" + location.host + "/ad" + window.location.search.replace('?','/');
        }
        else{
            console.log('Неверная связка логин/пароль');
        }
      })
      .fail(function(data) {
            console.log(data);
            console.log('Неполадки в соединении с сервером!');
      });
}
function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}