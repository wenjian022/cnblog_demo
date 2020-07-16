// 标签页
$('#myTab a').click(function () {
var new_tab = $(this).attr('aria-controls')
var old_tab =  $($('#myTab [class=active]').children()[0]).attr('aria-controls')

$('.tab-content #'+old_tab).removeClass('active')
$('#myTab [class=active]').removeClass('active')
$(this).parent().attr('class','active')
$('#'+new_tab).addClass('active')

})