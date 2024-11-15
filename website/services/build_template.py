class BuildTemplate:

    def build_for_front(questions, answers=None):
        template = {}
        answer_dict = {}

        if answers:
            answer_dict = {str(answer.get('question')).strip(): answer for answer in answers}
             
        for question in questions:
            question_id = str(question.get('_id')).strip()
            module = question.get('module')
            if module not in template:
                template[module] = []
            
            answer = answer_dict.get(question_id, None)
            if answer:
                template[module].append({
                    question.get('description'): answer.get('answer'),
                    "notes": answer.get('notes'),
                    "glossary": question.get('glossary'),
                    "question_id": question_id
                })
            else:
                template[module].append({
                    question.get('description'): None,
                    "notes": "",
                    "glossary": question.get('glossary'),
                    "question_id": question_id
                })
        
        return template
    
    def build_to_save():
        pass