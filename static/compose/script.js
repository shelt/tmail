window.onload = function() {
    // Highlight current sidelink selection
    setSidelink(document.getElementById("sidelink-compose"));
    
    // Reply-mode stuff
    var RECIPS_REPLYALL = document.getElementById("recips_replyall").content.split(",");
    var RECIPS_REPLYTO = document.getElementById("recips_replyto").content.split(",");
    var RECIP_SENDER = document.getElementById("recip_sender").content.split(",");
    var recips = [];
    
    if (typeof RECIP_SENDER !== null) { // This message is a reply
        if (Query["is_reply_all"] === "True") // And it's reply-all
            toList_set(RECIPS_REPLYALL,document.getElementById("r_reply_all"));
        else
            toList_set(RECIPS_REPLYTO,document.getElementById("r_reply_to"));
        
        document.getElementById("r_reply_all").onclick = function() {toList_set(RECIPS_REPLYALL,this);}
        document.getElementById("r_reply_to").onclick = function() {toList_set(RECIPS_REPLYTO,this);}
        document.getElementById("r_sender").onclick = function() {toList_set(RECIP_SENDER,this);}
    }
    
    //old todo
    //if (typeof recips_replyall !== "undefined") {
      //  radioChange(document.getElementById("r_reply_all"));
    //    setToList(recips_replyall); // recips_replyall is set inline
    //}
    
    // Enter keypress listener
    document.getElementById("addrecip").onkeypress = function(event) {
        if (event.which == 13 || event.keyCode == 13) {
            if (isValidEmail(this.value) == true) {
                addRecip(this.value);
                this.value = "";
                this.style.borderColor = "";
                radioChange();
            }
            else { 
                this.style.borderColor = "red";
            }
        }
    }
}



//////////////////////////
// TO-LIST MANIPULATING //
//////////////////////////
// The actual to-list is stored in the recips array.
// These functions first update the array, then update
// the DOM to reflect the array.

function toList_set(list, elem) {
    // Data-wise
    recips = list;

    // DOM-wise
    var toList = document.getElementById("recips");
    toList.innerHTML = "";
    for(var i=0; i<recips.length; i++) {
        var li = document.createElement("li");
        var text = document.createTextNode(recips[i]);
        li.appendChild(text);
        toList.appendChild(li);
        // TODO <div class="recip-remove" onclick="recipRemove('{recip}')">X</div>
    }
    
    // Highlight radio button
    radioChange(elem);
}
function toList_append(value) {
    // Data-wise
    recips.append(value);
    // DOM-wise
    var li = document.createElement("li");
    var text = document.createTextNode(value);
    li.appendChild(text);
    document.getElementById("recips").appendChild(li);
    
    // Highlight radio button
    radioChange(null);
    
}
function toList_drop(value) { // TODO
    document.getElementById("recips");
    
    // Highlight radio button
    radioChange(null);
}

// [called by]: toList_set, toList_append, toList_drop
// Sets the selected highlighted reply-mode. (Purely cosmetic)
function radioChange(elem) {
    if (elem === null) { // Unset highlight
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


///////////////////
// MISCELLANEOUS //
///////////////////

function isValidEmail(email) {
    var re = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/i;
    return re.test(email);
}

// Get GET parameter from location
var Query = (function(){
    var query = {}, pair, search = location.search.substring(1).split("&"), i = search.length;
    while (i--) {
        pair = search[i].split("=");
        query[pair[0]] = decodeURIComponent(pair[1]);
    }
    return query;
})();

