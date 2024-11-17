from fpdf import FPDF

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
                    question.get('description'): "",
                    "notes": "",
                    "glossary": question.get('glossary'),
                    "question_id": question_id
                })
        
        return template
    
    def build_to_save(form_data):
        answers = []
        for key, value in form_data.items():
            if key.startswith("answer_") or key.startswith("notes_"):
                parts = key.split('_')
                question_id = parts[1]
                field = parts[0]

                # Procurar a questão pelo ID
                question_data = next((item for item in answers if item["question"] == question_id), None)
                if not question_data:
                    question_data = {"question": question_id, "answer": None, "notes": ""}
                    answers.append(question_data)

                if field == "answer":
                    if value == "True":
                        question_data["answer"] = True
                    elif value == "False":
                        question_data["answer"] = False
                    elif value == "None":
                        question_data["answer"] = None
                elif field == "notes":
                    question_data["notes"] = value

        return answers
    
    def build_pdf(template, name, created_at, updated_at):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adicionar título e informações do checklist
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(200, 10, txt=name, ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Data de criação: {created_at}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Data de atualização: {updated_at}", ln=True, align='L')
        pdf.ln(10)

        # Adicionar módulos e perguntas
        for module, questions in template.items():
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt=module, ln=True, align='L')
            pdf.set_font("Arial", size=12)
            for question in questions:
                question_text = list(question.keys())[0]
                answer = question.get('answer', '')
                notes = question.get('notes', '')
                glossary = question.get('glossary', '')
                pdf.cell(200, 10, txt=f"P: {question_text}", ln=True, align='L')
                pdf.cell(200, 10, txt=f"R: {answer}", ln=True, align='L')
                pdf.cell(200, 10, txt=f"Anotações: {notes}", ln=True, align='L')
                pdf.cell(200, 10, txt=f"Glossário: {glossary}", ln=True, align='L')
                pdf.ln(5)

        return pdf.output(dest='S').encode('latin1')

        