window.onload = function() {
    // Highlight current box selection
    var __parts = window.location.pathname.split("?");
    var path = __parts[0].split("/");

    if (path[1] === "box") {
        setSidelink(document.getElementById("sidelink-"+ path[2] +"box"));
    }
    else if (path[1] === "compose") {
        if (typeof recip_sender !== "undefined")
            setToList(recip_sender);
        setSidelink(document.getElementById("sidelink-compose"));
    }    
}

function setSidelink(elem) {
    elem.style.backgroundColor = "#DDD";
    elem.style.boxShadow = "inset 0 0 3px #888";
}


function refresh() {
    document.refresh.submit();
}

var HIDDEN = ["msgid","cc","bcc"];
function toggleExtended(msgid) {
    for (var i = 0; i < HIDDEN.length; i++) {
        elem = document.getElementById(HIDDEN[i] + "-" + msgid);
        elem.style.display = elem.style.display === 'none' ? '' : 'none';
    }
}






// To List
setToList = function(list) {
    var toList = document.getElementById("recips");
    toList.innerHTML = "";
    for(var i=0; i<list.length; i++) {
        var li = document.createElement("li");
        var text = document.createTextNode(list[i]);
        li.appendChild(text);
        toList.appendChild(li);
        // TODO <div class="recip-remove" onclick="recipRemove('{recip}')">X</div>
    }
}

// This function can be called with no parameters to
// Disable
function radioChange(elem) {
    if (typeof elem === "undefined") {
        var labels = document.getElementById("replymode-fieldset").children[0].children;
        for (var i=0; i<labels.length; i++)
            if (labels[i].getAttribute("class") === "selected")
                labels[i].setAttribute("class","");
    }
    else {
        var labels = elem.parentElement.parentElement.children;
        for (var i=0; i<labels.length; i++)
            if (labels[i].getAttribute("class") === "selected")
                labels[i].setAttribute("class","");
            elem.parentNode.setAttribute("class","selected");
    }
}

function addRecip(elem) {
    // keypress TODO
    var li = document.createElement("li");
    var text = document.createTextNode(elem.value);
    li.appendChild(text);
    document.getElementById("recips").appendChild(li);
}





function addCustomRecipient() {
    if (arrValues.indexOf('Sam') > -1)
        alert("todo");
}
