$(document).ready(function () {
    $("#delete_entity_block").dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            height: 230,
            width: 450,
            closeText: 'hide'
        }
    );

    $("#delete_entity_block .cancel_link").bind("click", function() {
        $("#delete_entity_block").dialog("close");
        $('#delete_entity_block').data("action_element").value = "";
        return false;
    });


    $("#ok_button").bind("click", function() {
        $("#delete_entity_block").dialog("close");
        var allIds = $('#delete_entity_block').data("allIds");
        var entity_type = $('#delete_entity_block').data("entity_type");
        var path = $(this).attr("href");
        post_data = {'all_ids':allIds.join(';'), 'entity_type':entity_type}
        if ($("#project_name").length)
            post_data.project = $("#project_name").val();
        $.post("/entity/delete/", post_data,
            function (json_response) {
                var response = $.parseJSON(json_response);
                if (response.success) {
                    window.location.href = path;
                }
            }
        );
        return false;
    });

    $('.action').change(function () {
        $('#error').hide();
        var allIds = getEntityIdsToBeDeleted(this);
        var entity_type = getEntityType(this);
        var action = getActionValue(this);
        if (allIds.length == 0) {
            $('<div class="message-box" id="error">' + gettext('Please select atleast 1 subject') + '</div>').insertAfter($(this));
            $(this).val("--");
            return;
        }
        if (action == 'edit') {
            if (allIds.length > 1) {
                $('<div class="message-box" id="error">' + gettext('Please select only 1 subject') + '</div>').insertAfter($(this));
                $(this).val("--");
                return;
            }
            else {
                location.href = getEditURL() + entity_type + '/' + allIds[0] + '/';
            }

        }
        else if(action==""){
            return;
        }
        else{
            warnThenDeleteDialogBox(allIds, entity_type, this);
        }
    });


});

function warnThenDeleteDialogBox(allIds, entity_type, action_element) {
    $("#delete_entity_block").data("allIds", allIds);
    $("#delete_entity_block").data("entity_type", entity_type);
    $("#delete_entity_block").data("action_element", action_element);

    $("#delete_entity_block").dialog("open");
}
