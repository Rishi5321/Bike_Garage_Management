import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))


def get_garage_context():
    from app.models import Customer, Bike, Service, Bill, SparePart

    total_customers  = Customer.query.count()
    total_bikes      = Bike.query.count()
    pending_services = Service.query.filter_by(status='pending').count()
    completed        = Service.query.filter_by(status='completed').count()

    low_stock_parts  = SparePart.query.filter(
        SparePart.stock <= SparePart.min_stock
    ).all()
    low_stock_info   = ", ".join(
        [f"{p.name} ({p.stock} left)" for p in low_stock_parts]
    ) or "None"

    today_bills   = Bill.query.filter_by(paid=True).all()
    total_revenue = sum(b.total_amount for b in today_bills)

    recent_services = Service.query.order_by(
        Service.service_date.desc()
    ).limit(5).all()
    recent_info = ", ".join(
        [f"{s.bike.bike_number} - {s.service_type} ({s.status})"
         for s in recent_services]
    )

    context = f"""
    You are a helpful assistant for a bike repair garage management system.
    Answer questions based on the following current garage data:

    - Total Customers    : {total_customers}
    - Total Bikes        : {total_bikes}
    - Pending Services   : {pending_services}
    - Completed Services : {completed}
    - Total Revenue      : Rs {total_revenue}
    - Low Stock Parts    : {low_stock_info}
    - Recent Services    : {recent_info}

    You can answer questions about:
    - Customer and bike counts
    - Service status and history
    - Inventory and stock levels
    - Revenue and billing
    - General bike maintenance advice
    - How to use the garage management system

    Keep answers short, clear and helpful.
    If asked something outside garage context, politely say you can only
    help with garage related queries.
    Always respond in English.
    """
    return context


def ask_chatbot(user_message):
    try:
        context  = get_garage_context()
        response = client.chat.completions.create(
            model    = "llama-3.1-8b-instant",
            messages = [
                {"role": "system", "content": context},
                {"role": "user",   "content": user_message}
            ],
            max_tokens  = 500,
            temperature = 0.7
        )
        return {
            "success" : True,
            "reply"   : response.choices[0].message.content
        }
    except Exception as e:
        return {
            "success" : False,
            "reply"   : f"Sorry, I could not process your request. Error: {str(e)}"
        }