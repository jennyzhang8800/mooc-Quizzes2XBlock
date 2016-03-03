/* Javascript for Quizzes2XBlock. */
function Quizzes2XBlock(runtime, element) {

    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'getQuestionAndStudentStatus'),
            data: JSON.stringify({'hello': 'world'}),
            success: function(data) {
                console.info(data);
            }
        });
    });
}
