window.onload = function() {
    // Highlight current sidelink selection
    var __parts = window.location.pathname.split("?");
    var path = __parts[0].split("/");
    setSidelink(document.getElementById("sidelink-"+ path[2] +"box"));
}