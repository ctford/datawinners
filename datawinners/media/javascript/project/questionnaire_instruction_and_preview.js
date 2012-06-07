DW.instruction_and_preview = function (preview_url, preview_navigation_item) {
    this.preview_url = preview_url;
    this.preview_navigation_item = preview_navigation_item;
};

DW.instruction_and_preview.prototype = {
    bind_preview_navigation_item:function () {
        var that = this;
        $(this.preview_navigation_item).live('click', function () {
            return function(load_preview) {
                if (DW.questionnaire_form_validate()) {
                    load_preview.apply(that);
                }
            }(that.load_preview_content);
        });
    },

    load_preview_content:function () {
        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),
                         'question-set':JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2),
                         'profile_form':basic_project_info.values(),
                         'project_state':"Test"};

        var that = this;
        $.post(this.preview_url, post_data, function (response_data) {
            $("#questionnaire_content").html(response_data);
            $("#questionnaire_preview_instruction").show();
            $(that.preview_navigation_item).addClass("shadow-background");
        }, 'html');
    }
};

DW.instruction_and_preview.bind_cancel_button = function() {
    $(".close_preview").live('click', function() {
        $("#questionnaire_content").html("");
        $("#questionnaire_preview_instruction").hide();
        $(".shadow-background").removeClass("shadow-background");
    });
};

$(function () {
    var sms_preview = new DW.instruction_and_preview(sms_preview_link, '.navigation-sms-preview');
    sms_preview.bind_preview_navigation_item();
    var web_preview = new DW.instruction_and_preview(web_preview_link, '.navigation-web-preview');
    web_preview.bind_preview_navigation_item();
    DW.instruction_and_preview.bind_cancel_button();
});