const fs = require('fs');
let filename = "console.txt";

// Toggle for Console Input Field
$(document).ready(function(){
    $(".consoleInput").hide();
    $(".showHideCheck").on("change", function() {
        var $this = $(this);
        var $input = $this.parent().find(".consoleInput");
        if($this.is(":checked")) {
            $input.slideDown();
        } else {
            $input.slideUp();
        }
    });
});



// Console Input Handler
function consoleSubmission(event) {
    if (event.keyCode == 13) {
        var consoleOutput = document.getElementById("consoleInput").value;
        let data = {
            "console": consoleOutput
        }
        

        let ajax = $.ajax({
            type: "POST",
            url: "/test",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        });

    }
    else {
        document.getElementById('testButton').innerHTML = "This is a test";
    }
}
  

document.getElementById("consoleInput").addEventListener("keypress", consoleSubmission)


// Console Manual Popup
document.getElementById('popupTrigger').addEventListener('click', function() {
    document.getElementById('popup').style.display = "block";
});

// onclick event handler
window.onclick = function(event) {
    if (event.target == document.getElementById('popup')) {
        document.getElementById('popup').style.display = "none";
    }
    if (event.target == document.getElementById('popup2')) {
        document.getElementById('popup2').style.display = "none";
    }
}

// Delete button Popup
document.getElementById('popupTrigger2').addEventListener('click', function() {
    document.getElementById('popup2').style.display = "block";
});
