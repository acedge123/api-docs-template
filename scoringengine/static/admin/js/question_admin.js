jQuery(document).ready(function($) {
    let questionTypeSelect = $('select[id="id_type"]');
    let minMaxValueFields = $('.field-min_value, .field-max_value');
    let choicesGroup = $('#choices-group');

    function configureForQuestionType (){
        minMaxValueFields.addClass('required')

        switch (questionTypeSelect.val()) {
            case 'CH':
                minMaxValueFields.hide();
                choicesGroup.show();
                break
            case 'S':
                minMaxValueFields.show();
                choicesGroup.hide();
                break
            case 'O':
                minMaxValueFields.hide();
                choicesGroup.hide();
                break
            default:
                minMaxValueFields.hide();
                choicesGroup.hide();
        }
    }

    configureForQuestionType();

    questionTypeSelect.change(function(){
        configureForQuestionType();
    });
});
