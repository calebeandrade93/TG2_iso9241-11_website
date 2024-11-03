
class BuildTemplate:

    def build(questions, answers):
        template = {}
        for question in questions:
            question_id = str(question.get('_id')).strip()
            for answer in answers:
                answer_question = str(answer.get('question')).strip()
                if question_id == answer_question:
                    module = question.get('module')
                    if module not in template:
                        template[module] = []
                    template[module].append({
                        question.get('description'): answer.get('answer'),
                        "notes": answer.get('notes'),
                        "glossary": question.get('glossary')
                    })
        return template