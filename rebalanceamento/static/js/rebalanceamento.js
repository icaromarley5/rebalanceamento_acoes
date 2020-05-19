$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

function updateForm(form, index, prefix) {
    $(form).find(':input').each(function() {
        for (attr of ['name', 'id', 'data-select2-id']){
            if ($(this).attr(attr)){
                $(this).attr(
                    attr,
                    $(this).attr(attr).replace(prefix, index)
                )
            }
        }
    })
}

$('.delete-row').click(function() {
    if ($('.dynamic-form').length > 2 && $('.blocked').length == 0){
        // block edition
        $('.walletForm').addClass('blocked')

        element = $(this).parent().parent()
        rowName = element.find('select').attr('name')
        rowId = parseInt(rowName.match('\\d+')[0])

        nextForms = element.nextAll()

        element.hide(400)
        setTimeout(function(){
            element.find('select').select2('destroy')
            element.remove()
        
            // rebind select2 by deleting and adding new forms
            tickerList = []
            nextForms.each(function (){
                select = $(this).find('select')   
                if (select.length > 0){
                    // getting data 
                    idPrefix = '#id_form-' + (rowId + 1)
                    ticker = $(this).find('span span span span').attr('title')
                    tickerList.push(ticker)
                    quant = $(this).find(
                        idPrefix + '-quantity').val()
                    percent = $(this).find(
                        idPrefix + '-percent').val()
                    
                    // deleting
                    $(this).find('select').select2('destroy')
                    $(this).empty()
                    
                    //creating new
                    rowAux = $('#formset-table-empty').clone(true)
                    
                    //fill
                    updateForm(
                        rowAux, 
                        '-' + rowId + '-',
                        '-__prefix__-'
                    )

                    rowAux.find(
                        'select').append(
                            '<option value="' + ticker + '">' + ticker + '</option>');
                    
                    idPrefix = '#id_form-' + (rowId)
                    rowAux.find(
                        idPrefix + '-quantity').attr('value', parseInt(quant))
                    rowAux.find(
                        idPrefix + '-percent').attr('value', parseInt(percent))

                    //adding
                    rowAux.find('td').appendTo($(this))

                }
                rowId++
            })
            // filling autocomplete
            i = 0   
            nextForms.each(function (){
                select = $(this).find('select')   
                if (select.length > 0){
                    ticker = tickerList[i]
                    select.val(ticker)
                    select.trigger('change');
                }
                i++
            })

            $('#id_form-TOTAL_FORMS').val(
            parseInt($('#id_form-TOTAL_FORMS').val()) - 1
            )
            //release block
            $('.walletForm').removeClass('blocked')
        }, 400);
    }
})

$('.add-row').click(function() {
    if ($('.blocked').length == 0) {
        index = $('#id_form-TOTAL_FORMS').val()
        newRow = $('#formset-table-empty').clone(true)
        updateForm(
            newRow, 
            '-' + index + '-',
            '-__prefix__-'
        )
        lastRow = $('.dynamic-form:last')
        lastRow.clone().appendTo('.walletForm')
        
        newRow.find('td').appendTo(lastRow)
        
        element = $('.dynamic-form').last().prev()
        element.css('display', 'none')
        element.show(500)

        $('#id_form-TOTAL_FORMS').val(
            parseInt($('#id_form-TOTAL_FORMS').val()) + 1
        )
    }
})