$(document).ready(function() {
    $(document).ajaxStop($.unblockUI);
    $(".sms_tester_form").dialog({
        autoOpen: false,
        width: 1200,
        modal: true,
        title: sms_tester_title,
        zIndex:1100,
        open: function(){
            $(".questionnaire_preview1").load(quessionarie_preview_link, function() {
                $('.printBtn').addClass('none');
                $('.displayText').hide();
            });
        }
    });
    $(".sms_tester").unbind('click').click(function() {
        $(".sms_tester_form").removeClass("none");
        $(".sms_tester_form").dialog("open");
        return false;
    });

    $("#send_sms").unbind('click').click(function() {
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px', zIndex:1000000}});
        $.post('/test_sms_submission/', {'message':$("#id_message").val(), 'content':$("#id_message").val(), 'test_mode':true}, function(response) {
                    $("#id_message").val(response);
                });
    });
    $("#clear_sms").unbind('click').click(function() {
                    $("#id_message").val("");
    });
    
});