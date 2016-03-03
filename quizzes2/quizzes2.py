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
    # 学生能够回答该问题的最大尝试次数
    maxTry = Integer(default=99, scope=Scope.content)
    # 学生当前已经尝试的次数
    tried = Integer(default=0, scope=Scope.user_state)
    # 学生的回答时候已经被批改
    graded = Boolean(default=False, scope=Scope.user_state)
    # 学生每次回答的记录
    answerList = List(default=[], scope=Scope.user_state)
    # 当前block保存的题目
    questionJson = Dict(default={}, scope=Scope.content)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the Quizzes2XBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/quizzes2.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/quizzes2.css"))
        frag.add_javascript(self.resource_string("static/js/src/quizzes2.js"))
        frag.initialize_js('Quizzes2XBlock')
        return frag

    @XBlock.json_handler
    def getQuestionAndStudentStatus(self, data, suffix=''):
        try:
            if not hasattr(self.runtime, "anonymous_student_id"):
                raise Exception('Cannot get anonymous_student_id in runtime', self.runtime)
            student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
            self.logger.info('getQuestionAndStudentStatus [student=(%s, %s)] [tried=%d] [maxTry=%d] [graded=%s] [qNo=%d]' % (
                student.email,
                student.username,
                self.tried,
                self.maxTry,
                self.graded,
                self.questionJson['q_number']
            ))
            return {
                'maxTry': self.maxTry,
                'tried': self.tried,
                'graded': False,    # TODO: 添加评分系统
                'gradeInfo': {},
                'student': student,
                'question': self.questionJson
            }
        except Exception as e:
            self.logger.exception('ERROR getQuestionAndStudentStatus %s' % str(e.args))
            return {'code': 1, 'dese': str(e.args)}

    @XBlock.json_handler
    def studentSubmit(self, data, suffix=''):
        try:
            student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
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

            t = datetime.datetime.now() + datetime.timedelta(hours=12)
            createtime = t.strftime('%Y-%m-%d:%H:%M:%S')
            content['answer'].append({'time': createtime, 'answer': data['answer']})
            self.logger.info('studentSubmit [content=%s]' % json.dumps(content))

        except Exception as e:
            self.logger.exception('ERROR student_submit %s' % str(e.args))
            return {'code': 1, 'dese': str(e.args)}

    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Quizzes2XBlock",
             """<quizzes2/>
             """),
            ("Multiple Quizzes2XBlock",
             """<vertical_demo>
                <quizzes2/>
                <quizzes2/>
                <quizzes2/>
                </vertical_demo>
             """),
        ]
