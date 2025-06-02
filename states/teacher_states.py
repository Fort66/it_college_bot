from aiogram.fsm.state import State, StatesGroup


class TeacherState(StatesGroup):
    telegram_id = State()
    telegram_name = State()
    name = State()
    email = State()
    success_registry = State()
    is_registry = State()
    not_found = State()

class DisciplineState(StatesGroup):
    start = State()
    create_discipline = State()
    edit_discipline = State()
    delete_discipline = State()
    is_delete = State()

class QuestionState(StatesGroup):
    start = State()
    create_quest = State()
    edit_quest = State()
    delete_quest = State()
    selected_quest = State()
    is_delete = State()


class AnswerState(StatesGroup):
    start = State()
    create_answer = State()
    add_answer = State()
    edit_answer = State()
    delete_answer = State()
    is_correct = State()
    check_right_answer = State()
    is_delete = State()


class GroupState(StatesGroup):
    start = State()
    create_group = State()
    edit_group = State()
    delete_group = State()
    is_delete = State()


class StudentListState(StatesGroup):
    start = State()
    create_student = State()
    edit_student = State()
    delete_student = State()
    is_delete = State()


class StudentState(StatesGroup):
    start = State()
    not_registry = State()
    is_registry = State()
    not_found = State()


class ExamState(StatesGroup):
    start = State()
    create_exam = State()
    edit_exam = State()
    delete_exam = State()