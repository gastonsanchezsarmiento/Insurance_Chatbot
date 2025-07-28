
def get_chatbot_response(question: str) -> str:
    responses = {
        "hello": "How may I help you today?",
        "help": "I can answer questions"
    }
    question_lower = question.lower()
    for key in responses:
        if key in question_lower:
            return responses[key]
    return "I'm not sure how to answer that. Could you repeating it?"