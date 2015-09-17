var recips_data = [];
var RECIPS_REPLYALL = [];
var RECIPS_REPLYTO = [];
var RECIPS_SENDER = [];

window.onload = function() {
    // Highlight current sidelink selection
    setSidelink(document.getElementById("sidelink-compose"));
    
    // Reply-mode stuff

    
    RECIPS_REPLYALL = document.getElementById("recips_replyall");
    if (RECIPS_REPLYALL !== null) { // This message is a reply
        RECIPS_REPLYALL = RECIPS_REPLYALL.content.split(",");
        RECIPS_REPLYTO = document.getElementById("recips_replyto").content.split(",");
        RECIP_SENDER = document.getElementById("recip_sender").content.split(",");
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
                toList_append(this.value);
                this.value = "";
                this.style.borderColor = "";
                if (RECIPS_REPLYALL !== null)
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
    var recips = document.getElementById("recips");
    // Make visible (which is the case if the list was previously empty)
    recips.style = "";

    // Set it Data-wise
    recips_data.length = 0;
    recips_data.push.apply(recips_data,list);

    // Set it DOM-wise
    recips.innerHTML = "";
    for(var i=0; i<recips_data.length; i++) {
   }
    
    if (RECIPS_REPLYALL !== null)
        // Highlight radio button
        radioChange(elem);
}
function toList_append(value) {
    // Make visible (which is the case if the list was previously empty)
    recips.style = "";

    toList_add(value,document.getElementById("recips");
    
    if (RECIPS_REPLYALL !== null)
        // Highlight radio button
        radioChange(null);
    
}
// This function is called by toList_append and toList_set.
function toList_add(value,list) {
 
    // Set it Data-wise
    list.push(value);
    // Set it DOM-wise
    var li = document.createElement("li");
    li.setAttribute("id",value);
    li.appendChild(document.createTextNode(value));

    //Add remove button
    var rem = document.createElement("div");
    rem.setAttribute("class", "recip-remove");
    rem.setAttribute("onclick", "alert('todo');");
    rem.appendChild(document.createTextNode("X"));
    li.appendChild(rem);
    recips.appendChild(li); 
}


}
function toList_drop(value) { // TODO
    document.getElementById("recips");
    
    if (RECIPS_REPLYALL !== null)
        // Highlight radio button
        radioChange(null);
}

// [called by]: toList_set, toList_append, toList_drop
// Sets the selected highlighted reply-mode. (Purely cosmetic)
function radioChange(elem) {
    if (elem === null || typeof elem === "undefined") { // Unset highlight
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

