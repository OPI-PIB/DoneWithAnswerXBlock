/* Dummy code to make sure events work in Workbench as well as
 * edx-platform*/
if (typeof Logger === 'undefined') {
    var Logger = {
        log: function(a, b) { return; }
    };
}

function update_knob(element, data) {
  if($('.done_onoffswitch-checkbox', element).prop("checked")) {
    $(".done_feedback", element).css("display", "");
  } else {
    $(".done_feedback", element).css("display", "none");
  }
    if($(".done_description",element).text() === "None") {
        $(".done_description", element).css("display", "none");
    }
    if($(".done_feedback",element).text() === "None") {
        $(".done_feedback", element).css("display", "none");
    }
}

function DoneWithAnswerXBlock(runtime, element, data) {
    $('.done_onoffswitch-checkbox', element).prop("checked", data.state);

    update_knob(element, data);
    var handlerUrl = runtime.handlerUrl(element, 'toggle_button');

    $(function ($) {
        $('.done_onoffswitch-checkbox', element).change(function(){
            var checked = $('.done_onoffswitch-checkbox', element).prop("checked");
            $.ajax({
                type: "POST",
                url: handlerUrl,
                data: JSON.stringify({'done':checked})
            });
            Logger.log("edx.done.toggled", {'done': checked});
            update_knob(element, data);
        });
    });
}
