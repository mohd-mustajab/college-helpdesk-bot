import json

def handler(request):
    try:
        body = json.loads(request.body or "{}")
        user_message = body.get("message", "")

        if not user_message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'message' field"})
            }

        # Example simple logic — replace with your actual chatbot logic
        if "course" in user_message.lower():
            reply = "You can find all courses on the college portal 📚."
        elif "admission" in user_message.lower():
            reply = "Admissions are open till 30th Nov! 🏫"
        else:
            reply = "I’m your College Helpdesk Bot 🤖. How can I assist you today?"

        return {
            "statusCode": 200,
            "body": json.dumps({"reply": reply})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
