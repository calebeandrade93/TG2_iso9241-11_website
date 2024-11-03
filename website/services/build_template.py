class BuildTemplate:

    def build(questions, answers):
        template = {}
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
                    "glossary": question.get('glossary')
                })
            else:
                template[module].append({
                    question.get('description'): None,
                    "notes": "",
                    "glossary": question.get('glossary')
                })
        
        return template