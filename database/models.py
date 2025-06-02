from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Float
)
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class TypeExam(Base):
    __tablename__ = "type_exam"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(100), nullable=False)

class Admins(Base):
    __tablename__ = "admins"

    id = Column(String(100), primary_key=True, index=True, autoincrement=False)
    username = Column(String(100))
    main_admin = Column(Boolean)

class Teachers(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100))
    text = Column(String(100), nullable=False)
    username = Column(String(100))
    email = Column(String(100), nullable=False)
    disciplines = relationship("Disciplines", back_populates="teachers", cascade="all, delete", passive_deletes=True)
    groups = relationship("Groups", back_populates="teachers", cascade="all, delete", passive_deletes=True)

class Disciplines(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(String(100), ForeignKey("teachers.id"), nullable=False)
    text = Column(String(100), nullable=False)
    teachers = relationship("Teachers", back_populates="disciplines")
    questions = relationship("Quests", back_populates="disciplines", cascade="all, delete", passive_deletes=True)
    tasks = relationship("Tasks", back_populates="disciplines", cascade="all, delete", passive_deletes=True)

class Quests(Base):
    __tablename__ = "quest"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    disciplines = relationship("Disciplines", back_populates="questions")
    answers = relationship("Answers", back_populates="questions", cascade="all, delete", passive_deletes=True)

class Answers(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("quest.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Integer, nullable=False)
    questions = relationship("Quests", back_populates="answers")

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    exampl = Column(Text)
    disciplines = relationship("Disciplines", back_populates="tasks")

class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    text = Column(String(100), nullable=False)
    teachers = relationship("Teachers", back_populates="groups")
    students = relationship("Students", back_populates="groups", cascade="all, delete", passive_deletes=True)

class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(100))
    username = Column(String(100))
    text = Column(String(100), nullable=False)
    email = Column(String(100))
    groups = relationship("Groups", back_populates="students")

# class DateExam(Base):
#     __tablename__ = "date_exam"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     date = Column(DateTime, nullable=False)
#     discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
#     group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
#     type_exam_id = Column(Integer, ForeignKey("type_exam.id"), nullable=False)
#     amount_quest = Column(Integer, nullable=False)
#     amount_task = Column(Integer, default=0)
#     time_exam = Column(Integer, nullable=False)
#     time_start = Column(DateTime)

