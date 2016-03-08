/* Javascript for Quizzes2XBlock. */

String.prototype.replaceInFormat = function(repl) {
    return this.replace(/\{(\w+)\}/g, function(match, capture) {
        return repl[capture];
    });
};

function Quizzes2XBlock(runtime, element) {
    var curStatus;
    $.ajax({
        type: 'POST',
        url: runtime.handlerUrl(element, 'getCurrentStatus'),
        data: JSON.stringify({'data':'getCurrentStatus'}),
        dataType: 'json',
        success: function(data) {
            curStatus = data.result;
            onDataLoad();
        }
    });

    $(element).on('click', '.btn-submit', function(event) {
        answer = getStudentAnswer();
        if ($.trim(answer) == '') {
            alert('答案不能为空');
            return;
        }
        switchStyle($(event.target), 'submiting');
        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'studentSubmit'),
            data: JSON.stringify({'answer': answer}),
            dataType: 'json',
            success: function(data) {
                switchStyle($(event.target), 'submited');
                if (data.code != 0) {
                    alert('您的提交可能失败了' + JSON.stringify(data));
                }
            }
        });
    });

    function getStudentAnswer() {
        if (curStatus.question.options == undefined) {
            return $('.text-input', element).val();
        } else {
            var answer = '';
            $('.check-input:checked', element).each(function() {
                answer += $(this).val();
            });
            return answer;
        }
    };

    function switchStyle($el, style) {
        $el.attr('class', 'btn');
        $el.attr('disabled', false);
        if (style == 'submit') {
            $el.addClass('btn-submit');
            $el.text('再次提交');
        } else if (style == 'submiting') {
            $el.addClass('btn-submiting');
            $el.text('正在提交...');
            $el.attr('disabled', true);
        } else if (style == 'submited') {
            $el.addClass('btn-submited');
            $el.text('已提交');
            $el.attr('disabled', true);
        }
    }

    function onDataLoad() {
        console.info(curStatus);
        var source = $('#quizzes2-template', element).html();
        var template = Handlebars.compile(source);
        var html = template(curStatus);
        $('div.quizzes2_block', element).html(html);
    }
}

Handlebars.registerHelper('CheckLabel', function(typeStr, qNo, opt) {
    var TYPE_DEF = {
        'single_answer': 'radio',
        'true_false': 'radio',
        'multi_answer': 'checkbox'
    };
    return new Handlebars.SafeString(
        '<input type="{type}" name="option-{qNo}" class="check-input" value="{value}"/>{option}'.replaceInFormat({
            type: TYPE_DEF[typeStr],
            qNo: qNo,
            value: opt.split('.')[0],
            option: opt
        })
    );
});

Handlebars.registerHelper('Lastest', function(answer) {
    return answer[answer.length - 1]['answer'];
});

Handlebars.registerHelper('SubmitAction', function(tried, maxTry, answerd, graded) {
    var remain = maxTry - tried;
    var tryStr = '';
    if (graded) {
        tryStr = '已经批改,无法提交';
    } else if (maxTry == 0) {
        tryStr = '<span>该题不限提交次数</span>';
    } else if (remain > 0) {
        tryStr = '还可以再提交<span>' + remain + '</span>次';
    } else {
        tryStr = '已经用完所有次数';
    }

    var submitBtn = '';
    if (answerd) {
        if ((remain == 0 && maxTry != 0) || (graded)) {
            submitBtn = '<button class="btn btn-submited" disabled>已提交</button>';
        } else {
            submitBtn = '<button class="btn btn-submit">再次提交</button>';
        }
    } else {
        submitBtn = '<button class="btn btn-submit">提交</button>';
    }

    return new Handlebars.SafeString(
        submitBtn + '<p class="check-info">' + tryStr + '</p>'
    );
});

Handlebars.registerHelper('GradeInfo', function(graded, gradeInfo) {
    if (!graded) {
        return '该题尚未批改';
    } else {
        return '参考答案:' + gradeInfo.rightAnswer + ', 得分:' + gradeInfo.score;
    }
});

Handlebars.registerHelper('TypeText', function(type) {
    TYPE_STR = {
        'single_answer': '单选题',
        'multi_answer': '多选题',
        'true_false': '判断题',
        'question_answer': '问答题',
        'fill_in_the_blank': '填空题'
    };
    return TYPE_STR[type];
});
