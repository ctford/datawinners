//DW is the global name space for DataWinner

DW.instruction_template = {
    "number":gettext("Answer must be a number."),
    "min_number":gettext("Answer must be a number. The minimum is %d."),
    "max_number":gettext("Answer must be a number. The maximum is %d."),
    "range_number":gettext("Answer must be a number between %d-%d."),
    "text":gettext("Answer must be a word"),
    "max_text":gettext("Answer must be a word %d characters maximum"),
    "date":gettext("Answer must be a date in the following format: %s. Example: %s"),
    "single_select":gettext("Choose 1 answer from the list. Example: a"),
    "multi_select":gettext("Choose 1 or more answers from the list. Example: a or ab "),
    "gps":gettext("Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy Example: -18.1324,27.6547 "),
    "dd.mm.yyyy":"25.12.2011",
    "mm.dd.yyyy":"12.25.2011",
    "mm.yyyy":"12.2011"

};
DW.date_template = {
    "dd.mm.yyyy":gettext("day.month.year"),
    "mm.dd.yyyy":gettext("month.day.year"),
    "mm.yyyy":gettext("month.year")

};
DW.question = function (question) {
    var question_name = DW.next_question_name_generator();
    var defaults = {
        name:question_name,
        code:"code",
        required:true,
        type:"text",
        language:'en',
        choices:[],
        entity_question_flag:false,
        length_limiter:"length_unlimited",
        length:{
            min:1,
            max:""
        },
        range:{
            min:"",
            max:""
        },
        label:{
            en:"Question",
            fr:"Question"
        },
        date_format:"mm.yyyy",
        instruction:gettext("Answer must be a text"),
        newly_added_question:false,
        event_time_field_flag:false
    };

    // Extend will override the default values with the passed values(question), And take the values from defaults when its not present in question
    //first argument "true" in extend field shows that appent values in default
    this.options = $.extend(true, defaults, question);
    this._init();
};

DW.initChoices = function (choices, language) {
    var final_choices = [];
    if (!language) {
        language = questionnaireViewModel.language;
    }
    $.each(choices, function (index, choice) {
        var display_choice = {};
        display_choice['text'] = choice.text[language];
        display_choice['val'] = choice.val;
        final_choices.push(display_choice);
    });
    return final_choices;
};

DW.question.prototype = {
    _init:function () {
        var q = this.options;
        this.newly_added_question = ko.observable(q.newly_added_question);
        this.range_min = ko.observable(q.range.min);
        this.event_time_field_flag = ko.observable(q.event_time_field_flag);

        //This condition required especially because in DB range_max is a mandatory field
        this.range_max = ko.observable(q.range.max);

        this.min_length = ko.observable(q.length.min);
        this.max_length = ko.observable(q.length.max);
        if (DW.isRegistrationQuestionnaire()) {
            this.name = ko.observable(q.name);
            this.title = ko.observable(q.label[questionnaireViewModel.language]);
        } else {
            this.title = ko.observable(q.name);
        }
        this.code = ko.observable(q.code);
        this.type = ko.observable(q.type);
        this.required = ko.observable(q.required);

        var initialValues = DW.initChoices(q.choices, q.language);
        this.choices = ko.observableArray(initialValues);
        this.is_entity_question = ko.observable(q.entity_question_flag);
        this.date_format = ko.observable(q.date_format);
        this.length_limiter = ko.observable(q.length.max ? "length_limited" : "length_unlimited");
        this.instruction = ko.dependentObservable({
            read:function () {
                if (this.type() == "text") {
                    if (this.max_length() != "" && this.max_length() > 0) {
                        return $.sprintf(DW.instruction_template.max_text, this.max_length());
                    }
                    return DW.instruction_template.text;
                }
                if (this.type() == "telephone_number") {
                    return $.sprintf(DW.instruction_template.max_text, "15");
                }
                if (this.type() == "list") {
                    return DW.instruction_template.text;
                }
                if (this.type() == "integer") {
                    if (this.range_min() == "" && this.range_max() == "") {
                        return DW.instruction_template.number;
                    }
                    if (this.range_min() == "") {
                        return $.sprintf(DW.instruction_template.max_number, this.range_max());
                    }
                    if (this.range_max() == "") {
                        return $.sprintf(DW.instruction_template.min_number, this.range_min());
                    }
                    return $.sprintf(DW.instruction_template.range_number, this.range_min(), this.range_max());
                }
                if (this.type() == "date") {
                    return $.sprintf(DW.instruction_template.date, DW.date_template[this.date_format()], DW.instruction_template[this.date_format()]);
                }
                if (this.type() == "geocode") {
                    return DW.instruction_template.gps;
                }
                if (this.type() == "select1") {
                    return DW.instruction_template.single_select;
                }
                if (this.type() == "select") {
                    return DW.instruction_template.multi_select;
                }
                return "No instruction can be generated";
            },
            owner:this
        });
        this.canBeDeleted = function () {
            if (DW.isRegistrationQuestionnaire()) {
                return (!this.is_entity_question() && this.name() != 'name');
            } else {
                return (!this.is_entity_question());
            }
        };
        this.isEnabled = function () {
            return this.newly_added_question();
        };


        this.isAChoiceTypeQuestion = ko.dependentObservable({
            read:function () {
                return this.type() == "select" || this.type() == "select1" ? "choice" : "none";
            },
            write:function (value) {
                this.type(this.type() == "" ? "select" : "select1");
            },
            owner:this
        });
    }

};


DW.change_question_title_for_reporting_period = function (replaceto, replacewith) {
    $(questionnaireViewModel.questions()).each(function (question) {
        if (questionnaireViewModel.selectedQuestion().event_time_field_flag()) {
            var question_title = questionnaireViewModel.selectedQuestion().title();
            questionnaireViewModel.selectedQuestion().title(question_title.replace(replaceto, replacewith));
        }
    });
    questionnaireViewModel.questions.valueHasMutated();
};


DW.removeQuestionCheckForRegistration = function (question) {
    $("#delete_warning").dialog("open");
    $("#delete_ok").unbind('click').click(function () {
        questionnaireViewModel.removeQuestion(question);
        $("#delete_warning").dialog("close");
    });
    $("#delete_cancel").unbind('click').click(function () {
        $("#delete_warning").dialog("close");
        return false;
    });
};

DW.removeQuestionCheckForSubmission = function (question) {
    var index = $.inArray(question, questionnaireViewModel.questions());
    if (questionnaireViewModel.questions()[index].event_time_field_flag()) {
        $("#delete_question").dialog("open");
    } else {
        questionnaireViewModel.removeQuestion(question);
    }
    $("#ok_button_que_change").unbind('click').click(function () {
        questionnaireViewModel.removeQuestion(question);
        $("#delete_question").dialog("close");
    });
    $("#cancel_link_que").unbind('click').click(function () {
        $("#delete_question").dialog("close");
        return false;
    });

};

DW.isRegistrationQuestionnaire = function () {
    return $('#qtype').val() == 'subject';
};

DW.next_question_name_generator = function () {
    return 'Question ' + ($('div.question_list ol li').length + 1);
};

DW.next_option_value = function (lastChoice) {
    var nextOption = "a";
    if (lastChoice.charCodeAt(lastChoice.length - 1) == 122) {
        if (lastChoice.length == 2) {
            nextOption = String.fromCharCode(lastChoice.charCodeAt(0) + 1) + "a";
        } else {
            nextOption = "1a";
        }
    } else {
        nextOption = (lastChoice.length == 2) ? lastChoice[0] : "";
        nextOption += String.fromCharCode(lastChoice.charCodeAt(lastChoice.length - 1) + 1);
    }
    return nextOption;
}

DW.report_period_date_format_change_warning = {
    old_date_format:"",
    is_continue:false,
    has_not_warning:true,
    init:function () {
        DW.report_period_date_format_change_warning.init_warning_dialog();
        DW.report_period_date_format_change_warning.bind_dialog_closed();
        DW.report_period_date_format_change_warning.bind_cancel_link();
        DW.report_period_date_format_change_warning.bind_continue();
    },
    init_warning_dialog:function () {
        $("#change_date_format_warning_message").dialog({
            title:gettext("Warning !!"),
            modal:true,
            autoOpen:false,
            height:200,
            width:400,
            closeText:'hide'
        });
    },

    bind_dialog_closed:function () {
        $("#change_date_format_warning_message").bind("dialogclose", function (event, ui) {
                if (!DW.report_period_date_format_change_warning.is_continue) {
                    var date_format = questionnaireViewModel.selectedQuestion().date_format();
                    $("input[value='" + date_format + "']").attr("checked", true);
                    DW.report_period_date_format_change_warning.is_continue = false;
                }
            }
        )
        ;

    },

    bind_cancel_link:function () {
        $("#change_date_format_cancel").bind("click", function () {
            var date_format = DW.report_period_date_format_change_warning.old_date_format;
            questionnaireViewModel.selectedQuestion().date_format(date_format);
            $("input[value='" + date_format + "']").attr("checked", true);
            DW.report_period_date_format_change_warning.is_continue = false;
            $("#change_date_format_warning_message").dialog("close");
        });

    },

    bind_continue:function () {
        $("#change_date_format_continue").bind("click", function () {
            DW.report_period_date_format_change_warning.is_continue = true;
            DW.report_period_date_format_change_warning.has_not_warning = false;
            $("#change_date_format_warning_message").dialog("close");
        });
    },

    show_warning:function () {
        $("#change_date_format_warning_message").dialog("open");
        DW.report_period_date_format_change_warning.is_continue = false;
    }

};

DW.change_date_format_for_reporting_period = function (date_format_element) {
    if (questionnaireViewModel.selectedQuestion().event_time_field_flag() && is_edit && DW.report_period_date_format_change_warning.has_not_warning) {
        DW.report_period_date_format_change_warning.show_warning();
    }
}