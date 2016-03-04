# coding:utf8
# luofuwen


class Config:
    # log config
    logFile = '/tmp/quizzes2_block.log'
    logFmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

    # 题库github配置
    getQuestionJsonUrl = 'https://api.github.com/repos/chyyuu/os_course_exercise_library/contents/data/json/%(qDir)d/%(qNo).json'
