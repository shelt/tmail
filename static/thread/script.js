var HIDDEN = ["msgid","cc","bcc"];
function toggleExtended(msgid) {
    for (var i = 0; i < HIDDEN.length; i++) {
        elem = document.getElementById(HIDDEN[i] + "-" + msgid);
        elem.style.display = elem.style.display === 'none' ? '' : 'none';
    }
}