# question module

import random


class Question:
    question_text: str
    correct_answer: str
    incorrect_answers: tuple

    def __init__(self, *args):
        self.question_text = args[0]
        self.correct_answer = args[1]
        self.incorrect_answers = args[2:5]

    def create_question(self) -> tuple:
        answers = [self.correct_answer, *self.incorrect_answers]
        shuffled = []
        correct_answer_index = 0
        for i in range(4):
            if len(answers) == 0:
                break
            x = random.randint(0, len(answers) - 1)
            shuffled.append(answers[x])
            if answers[x] == self.correct_answer:
                correct_answer_index = i
            answers.pop(x)
            print(answers, shuffled)

        print(shuffled)
        return tuple([self.question_text, *shuffled, correct_answer_index])


def read_questions(file_name: str) -> list[Question]:
    result = []
    with open(file_name, "rt") as f:
        for x in f:
            result.append(Question(*x.strip().split('\t')))
    return result

