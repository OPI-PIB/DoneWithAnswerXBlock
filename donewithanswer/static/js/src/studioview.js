/* Javascript for MarkAsDoneXBlock studio view. */
function DoneWithAnswerXBlockEdit(runtime, element) {
    $(element).find('.save-button').bind('click', function() {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        var data = {
            description: $(element).find('textarea[name=description]').val(),
            feedback: $(element).find('textarea[name=feedback]').val(),
            button_name: $(element).find('input[name=button_name]').val()
        };
        runtime.notify('save', {state: 'start'});
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
          runtime.notify('save', {state: 'end'});
        });
      });
    
      $(element).find('.cancel-button').bind('click', function() {
        runtime.notify('cancel', {});
      });

}
