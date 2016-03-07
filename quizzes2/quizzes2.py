# coding: utf8
# luofuwen
import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, Dict, List, Boolean
from xblock.fragment import Fragment
from conf import Config
from util import Util
import json
import datetime
import urllib2
import base64


class Test(object):
    pass


class Quizzes2XBlock(XBlock):
    """
    这是学生回答习题的，需要保存每个学生的回答状态
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    logger = Util.logger({
        'logFile': Config.logFile,
        'logFmt': Config.logFmt,
        'logName': 'Quizzes2XBlock'
    })

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )
    # 学生能够回答该问题的最大尝试次数,0表示无限制
    maxTry = Integer(default=0, scope=Scope.content)
    # 当前block保存的题目
    questionJson = Dict(default={}, scope=Scope.content)
    # 当前block保存的题题号
    qNo = Integer(default=0, scope=Scope.content)
    # 学生当前已经尝试的次数
    tried = Integer(default=0, scope=Scope.user_state)
    # 学生每次回答的记录
    answerList = List(default=[], scope=Scope.user_state)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the Quizzes2XBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/quizzes2.html")
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/quizzes2.css"))
        frag.add_javascript(self.resource_string("static/js/handlebars-v4.0.5.js"))
        frag.add_javascript(self.resource_string("static/js/src/quizzes2.js"))
        frag.initialize_js('Quizzes2XBlock')
        return frag

    def studio_view(self, context=None):
        html = self.resource_string("static/html/quizzes2_config.html")
        frag = Fragment(unicode(html).format(qNo=self.qNo, maxTry=self.maxTry))
        frag.add_javascript(self.resource_string('static/js/src/quizzes2_config.js'))
        frag.initialize_js('Quizzes2XBlock')
        return frag

    def dAnswer(self, question):
        '''
        用于删除题目中答案等相关信息
        '''
        question['answer'] = u'已隐藏'
        question['explain'] = u'已隐藏'
        return question

    def genCurrentStatus(self):
        if not hasattr(self.runtime, "anonymous_student_id"):
            raise Exception('Cannot get anonymous_student_id in runtime')
        student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        if type(self.questionJson) is str:
            self.questionJson = json.loads(self.questionJson)

        self.logger.info('CurrentStatus [student=(%s, %s)] [tried=%d] [maxTry=%d] [graded=%s] [qNo=%d]' % (
            student.email,
            student.username,
            self.tried,
            self.maxTry,
            False,
            self.questionJson['q_number']
        ))
        return {
            'maxTry': self.maxTry,
            'tried': self.tried,
            'graded': False,    # TODO: 添加评分系统
            'gradeInfo': {},
            'student': {'email': student.email, 'username': student.username},
            'answer': self.answerList,
            'question': self.questionJson
        }

    @XBlock.json_handler
    def getCurrentStatus(self, data, suffix=''):
        try:
            status = self.genCurrentStatus()
            return {'code': 0, 'desc': 'ok', 'result': status}
        except Exception as e:
            self.logger.exception('ERROR getCurrentStatus %s' % (str(e)))
            return {'code': 1, 'dese': str(e)}

    @XBlock.json_handler
    def studentSubmit(self, data, suffix=''):
        try:
            student = self.runtime.get_real_user(self.runtime.anonymous_student_id)

            t = datetime.datetime.now() + datetime.timedelta(hours=12)
            createtime = t.strftime('%Y-%m-%d:%H:%M:%S')
            answerItem = {'time': createtime, 'answer': data['answer']}
            self.answerList.append(answerItem)
            # 删除多余的历史数据
            if len(self.answerList) > Config.maxSizeOfAnswerList:
                self.answerList = self.answerList[-(Config.maxSizeOfAnswerList):]

            self.tried += 1

            # TODO 从gitlab读取content
            content = {
                'maxTry': self.maxTry,
                'tried': self.tried,
                'graded': False,
                'gradeInfo': {},
                'student': student,
                'question': self.questionJson,
                'answer': self.answerList
            }

            self.logger.info('studentSubmit [content=%s]' % json.dumps(answerItem))
            # TODO push to gitlab
            return {'code': 0, 'desc': 'ok', 'result': self.genCurrentStatus()}
        except Exception as e:
            self.logger.exception('ERROR student_submit %s' % str(e.args))
            return {'code': 1, 'dese': str(e.args)}

    @XBlock.json_handler
    def studioSubmit(self, data, suffix=''):
        '''
        用于配置XBlock的题目，以及每个学生的回答次数
        data.q_number   题号
        data.max_try    最大尝试的次数
        '''
        try:
            self.logger.info('studioSubmit data=%s' % str(data))
            # 保存max_try
            self.maxTry = int(data['maxTry'])

            # 从github获取题号对应的题目json数据
            q_number = int(data['qNo'])
            self.qNo = q_number
            url = Config.getQuestionJsonUrl % {
                'qDir': ((q_number - 1) / 100) + 1,
                'qNo': q_number,
            }
            res_data = urllib2.urlopen(url)
            res = res_data.read()
            res = json.loads(res)
            if 'content' in res:
                content = base64.b64decode(res['content'])
                self.questionJson = json.loads(content)
                self.logger.info('get question from remote [qNo=%s] [content="%s"]' % (q_number, content))
                return {'code': 0, 'desc': 'ok'}
            else:
                self.logger.warning('ERROR studioSubmit: Cannot read question json [qNo=%d] [msg=%s]' % (q_number, res['message']))
                return {'code': 2, 'desc': res['message']}
        except Exception as e:
            self.logger.exception('ERROR studioSubmit %s' % str(e.args))
            return {'code': 1, 'dese': str(e.args)}

    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Quizzes2XBlock",
             """<quizzes2/>
             """),
            ("Quizzes2XBlock-test",
                """
                <quizzes2 maxTry="2" questionJson='{"status":"ok","knowledge":["操作系统概述"],"degree_of_difficulty":1,"explain":"B\n","question":"批处理系统的主要缺点是 。\n","source":"网络","answer":"B","type":"single_answer","options":["A.CPU的利用率不高","B.失去了交互性","C.不具备并行性","D.以上都不是"],"q_number":1002}'/>
             """),
            ("Multiple Quizzes2XBlock",
             """<vertical_demo>
                <quizzes2 maxTry="2" questionJson='{"status":"ok","knowledge":["操作系统概述"],"degree_of_difficulty":1,"explain":"B\n","question":"批处理系统的主要缺点是 。\n","source":"网络","answer":"B","type":"single_answer","options":["A.CPU的利用率不高","B.失去了交互性","C.不具备并行性","D.以上都不是"],"q_number":1002}'/>
                <quizzes2 maxTry="5" questionJson='{"status":"error","knowledge":["文件系统"],"degree_of_difficulty":1,"explain":"解释\n","question":"文件的逻辑结构的基本形式有______________________________________ 。\n","source":"网络","answer":"解释\n","type":"fill_in_the_blank","q_number":396}'/>
                <quizzes2 maxTry="0" questionJson='{"status":"ok","knowledge":["调查问卷"],"degree_of_difficulty":1,"explain":"解释\n","question":"为什么要学这门课？\n","source":"网络","answer":"A","type":"multi_answer","options":["A.对内容有兴趣","B.内容与自己的目标相一致，结果有用","C.由于学分要求，必须选","D.其他，请注明原因"],"q_number":1137}' answerList='[{"time":"2012-01-01 13:20","answer":"A"}]'/>
                </vertical_demo>
             """),
        ]
