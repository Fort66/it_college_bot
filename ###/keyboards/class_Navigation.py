from functions.load_json_file import load_file
from keyboards.class_Keyboards import Keyboards


class Navigation:
    def __init__(self):
        self.teacher_nav_list = {
            'keyboards/teachers/main': {
                'keyboards/teachers/disciplines': None
            }
        }

        self.teacher_nav_list_index = 0

        self.student_nav_list = []
        self.student_nav_list_index = 0