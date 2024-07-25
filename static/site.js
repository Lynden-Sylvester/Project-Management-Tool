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


document.getElementById('popupTrigger').addEventListener('click', function() {
    document.getElementById('popup').style.display = "block";
});

window.onclick = function(event) {
    if (event.target == document.getElementById('popup')) {
        document.getElementById('popup').style.display = "none";
    }
}

document.getElementById('popupTrigger2').addEventListener('click', function() {
    document.getElementById('popup2').style.display = "block";
});

window.onclick = function(event) {
    if (event.target == document.getElementById('popup2')) {
        document.getElementById('popup2').style.display = "none";
    }
}