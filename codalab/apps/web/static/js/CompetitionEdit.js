$('document').ready(function () {
    // This helps make sections appear with Foundation
    $(this).foundation('section', 'reflow');

    var nextPage = 0;

    $(document).find("input[name*='_date']").datetimepicker({
        format: 'Y-m-d H:i:s',
        formatTime: 'H:i:s',
        formatDate: 'Y-m-d',
        value: $(this).val(),
        allowBlank: true,
        defaultSelect: false
    });

    // Hide order for everything < 2 
    $('#pages').find("[name*=rank]").each(function (index, value) {
        nextPage = Math.max(nextPage, parseInt(value.value) + 1);
        if (value.value <= 2) {
            $(value).parents(".fieldWrapper").hide();
        }
    });

    // Hide Category, it's not modifiable
    $('#pages').find("[name*=category]").each(function (index, value) {
        $(value).parents(".fieldWrapper").hide();
    });

    $('#pages').children('.empty-page-form').hide();
    pages = $('#pages').children('li').djangoFormset({
        formTemplateClass: 'empty-page-form'
    });

    pages.forms.each(function (index, form) {
        form.pDelete = form.delete;
        form.delete = function () {
            if (confirm("Are you sure you want to delete this page?")) {
                form.pDelete();
            }
        };
    });

    $('.add-page').click(function () {
        form = pages.addForm();
        form.elem.toggle();
        wlp = window.location.pathname.split("/");
        form.elem.find("[name$=container]").val(wlp[wlp.length - 1]);
        form.elem.find("[name*=rank]").parents(".fieldWrapper").show();
        form.elem.find("[name*=rank]").val(nextPage);
        nextPage += 1;
        form.pDelete = form.delete;
        form.delete = function () {
            if (confirm("Are you sure you want to delete this page?")) {
                form.pDelete();
            }
        };
    });

    // Dynamic adding/removing of phases
    $('#phases').children('.empty-phase-form').hide();
    phases = $('#phases').children('li').djangoFormset({
        formTemplateClass: 'empty-phase-form'
    });

    phases.forms.each(function (index, phase) {
        phase.pDelete = phase.delete;
        phase.delete = function () {
            if (confirm("Are you sure you want to delete this page?")) {
                phase.pDelete();
            }
        };
    });

    $('.add-phase').click(function () {
        form = phases.addForm();
        form.elem.toggle();
        form.elem.find('[name$=phasenumber]')[0].value = form.index;
        form.pDelete = form.delete;
        form.delete = function () {
            if (confirm("Are you sure you want to delete this page?")) {
                form.pDelete();
            }
        };
    });
});
