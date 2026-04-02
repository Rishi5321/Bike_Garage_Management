import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))


def get_full_garage_context():
    from app.models import Customer, Bike, Service, Bill, SparePart
    from datetime import date

    today = date.today()

    customers = Customer.query.all()
    customer_info = ""
    for c in customers:
        customer_info += f"""
        - Name: {c.name} | Phone: {c.phone} | Email: {c.email or 'N/A'} | Address: {c.address or 'N/A'}
          Bikes: {', '.join([b.bike_number + ' (' + b.bike_model + ')' for b in c.bikes]) or 'No bikes'}
        """

    bikes = Bike.query.all()
    bike_info = ""
    for b in bikes:
        bike_info += f"""
        - Bike: {b.bike_number} | Model: {b.bike_model} | Brand: {b.brand or 'N/A'} | Year: {b.year or 'N/A'}
          Owner: {b.customer.name} | Phone: {b.customer.phone}
          Total Services: {len(b.services)}
        """

    services = Service.query.order_by(Service.service_date.desc()).all()
    service_info = ""
    for s in services:
        service_info += f"""
        - Service: {s.service_type} | Bike: {s.bike.bike_number} | Owner: {s.bike.customer.name}
          Status: {s.status} | Cost: Rs {s.cost} | Date: {s.service_date.strftime('%d-%m-%Y')}
          Description: {s.description or 'N/A'}
        """

    pending_services  = [s for s in services if s.status == 'pending']
    completed_services = [s for s in services if s.status == 'completed']

    parts = SparePart.query.all()
    parts_info = ""
    for p in parts:
        status = "LOW STOCK" if p.stock <= p.min_stock else "In Stock"
        parts_info += f"""
        - Part: {p.name} | Category: {p.category or 'N/A'} | Price: Rs {p.price}
          Stock: {p.stock} | Min Stock: {p.min_stock} | Status: {status}
        """

    bills = Bill.query.order_by(Bill.created_at.desc()).all()
    bill_info = ""
    for b in bills:
        bill_info += f"""
        - Bill #{b.id} | Customer: {b.service.bike.customer.name} | Bike: {b.service.bike.bike_number}
          Service: {b.service.service_type} | Total: Rs {b.total_amount}
          Status: {'PAID' if b.paid else 'UNPAID'} | Date: {b.created_at.strftime('%d-%m-%Y')}
        """

    today_bills    = [b for b in bills if b.created_at.date() == today]
    today_revenue  = sum(b.total_amount for b in today_bills if b.paid)
    total_revenue  = sum(b.total_amount for b in bills if b.paid)
    total_unpaid   = sum(b.total_amount for b in bills if not b.paid)
    low_stock_parts = [p for p in parts if p.stock <= p.min_stock]

    context = f"""
You are a helpful assistant for a bike repair garage management system called Bike Garage.
You have access to complete real-time garage data. Answer any question accurately using this data.

===== SUMMARY =====
Today's Date         : {today.strftime('%d-%m-%Y')}
Total Customers      : {len(customers)}
Total Bikes          : {len(bikes)}
Total Services       : {len(services)}
Pending Services     : {len(pending_services)}
Completed Services   : {len(completed_services)}
Total Parts          : {len(parts)}
Low Stock Parts      : {len(low_stock_parts)}
Today's Revenue      : Rs {today_revenue}
Total Revenue (Paid) : Rs {total_revenue}
Total Unpaid Amount  : Rs {total_unpaid}
Total Bills          : {len(bills)}

===== ALL CUSTOMERS =====
{customer_info if customer_info else 'No customers yet'}

===== ALL BIKES =====
{bike_info if bike_info else 'No bikes registered yet'}

===== ALL SERVICES =====
{service_info if service_info else 'No services yet'}

===== ALL SPARE PARTS =====
{parts_info if parts_info else 'No parts added yet'}

===== ALL BILLS =====
{bill_info if bill_info else 'No bills generated yet'}

===== LOW STOCK ALERT =====
{', '.join([p.name + ' (' + str(p.stock) + ' left)' for p in low_stock_parts]) or 'All parts are well stocked'}

Instructions:
- Answer questions accurately using the above data
- If asked about a specific customer, bike, service or bill find it from the data above
- For revenue questions use the summary section
- Keep answers clear and helpful
- If something is not in the data say you do not have that information
- Always respond in English
"""
    return context


def ask_chatbot(user_message):
    try:
        context  = get_full_garage_context()
        response = client.chat.completions.create(
            model    = "llama-3.3-70b-versatile",
            messages = [
                {"role": "system", "content": context},
                {"role": "user",   "content": user_message}
            ],
            max_tokens  = 1000,
            temperature = 0.3
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
