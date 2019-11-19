
function Year() {
  var date = new Date();
  var year = date.getFullYear();
  
  for (var i= 2019; i>=year-120; i--){
  var option = document.createElement("option");
  var x = document.getElementById("year");
  	option.text=i;
    x.add(option);
  }
}
function Month() {
  for (var i= 1; i<=12; i++){
  var x = document.getElementById("month");
  var option = document.createElement("option");
  	option.text=i;
    x.add(option);
  }
}
function Day() {
  for (var i= 1; i<=31; i++){
  var x = document.getElementById("day");
  var option = document.createElement("option");
  	option.text=i;
    x.add(option);
  }
}
Year();
Month();
Day();