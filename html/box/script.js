window.onload = function() {
    // Highlight current box selection
    var _parts = window.location.pathname.split("/");
    var root = _parts[1];
    var box = _parts[2];
    if (root === "box") {
        current = document.getElementById("sidelink-"+ box +"box");
        current.setAttribute("background-color","#DDD");
        current.setAttribute("box-shadow", "inset 0 0 3px #888");
    }
}
