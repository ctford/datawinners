var questionnaireViewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,
    language:'en',

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.newly_added_question(true);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.hasAddedNewQuestions = true;
    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.questions.valueHasMutated();
    },
    canQuestionBeDeleted: function() {
        return questionnaireViewModel.questions().length > 2;
    },
    renumberQuestions: function(){
        var questionPattern = /^Question \d+$/;
        for (var i = 0; i < questionnaireViewModel.questions().length; i++){
            var question = questionnaireViewModel.questions()[i];
            if (questionPattern.test(question.title()) )
                question.title("Question " + (i + 1));
        }
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        questionnaireViewModel.questions.remove(question);
        if(questionnaireViewModel.questions().length == 0){
            questionnaireViewModel.addQuestion();
            return;
        }
        questionnaireViewModel.renumberQuestions();
        var next_index = (index) % questionnaireViewModel.questions().length;
        questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        questionnaireViewModel.hasAddedNewQuestions = true;
    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },
    showAddChoice:function() {
        if (questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (questionnaireViewModel.selectedQuestion().choices().length == 0) {
                questionnaireViewModel.addOptionToQuestion();
                questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats:function() {
        return questionnaireViewModel.selectedQuestion().type() == "date";
    },
    showAddRange:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function() {
        var selectedQuestionCode = "a";
        if (questionnaireViewModel.selectedQuestion().choices().length > 0) {
            var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
            selectedQuestionCode = DW.next_option_value(lastChoice.val);
        }
        questionnaireViewModel.selectedQuestion().choices.push({text:"", val:selectedQuestionCode});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'];//.charCodeAt(0);
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = lastChoiceValue;
            $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
            lastChoiceValue = DW.next_option_value(lastChoiceValue);//lastChoiceValue + 1;
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        if(question.event_time_field_flag()){
            DW.report_period_date_format_change_warning.old_date_format = question.date_format();
        }
        $(this).addClass("question_selected");
        if($("#question_title").hasClass("blue_frame")){
            $("#question_title").removeClass("blue_frame");
        }
        if($("#periode_green_message").length>0){
            $("#periode_green_message").hide();
        }
    },
    clearChoices: function() {
        questionnaireViewModel.selectedQuestion().choices([]);
    },
    showLengthLimiter: function() {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    set_all_questions_as_old_questions:function(){
        for (var question_index in questionnaireViewModel.questions()){
            questionnaireViewModel.questions()[question_index].newly_added_question(false)
        }
    },
    choiceCanBeDeleted: function() {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return questionnaireViewModel.selectedQuestion().isEnabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
    }
};