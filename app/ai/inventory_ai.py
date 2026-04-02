import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))


def get_inventory_context():
    from app.models import SparePart
    parts = SparePart.query.all()
    parts_info = ""
    for p in parts:
        parts_info += f"- ID:{p.id} | Name:{p.name} | Category:{p.category or 'N/A'} | Price:Rs {p.price} | Stock:{p.stock} | Min Stock:{p.min_stock}\n"
    return parts_info


def process_inventory_command(command):
    inventory = get_inventory_context()

    system_prompt = f"""
You are an AI assistant for a bike garage inventory management system.
You help the garage owner update stock using natural language commands.

Current Inventory:
{inventory}

Your job is to understand the owner's command and return a JSON response.

IMPORTANT RULES:
- Always respond with ONLY a valid JSON object
- No extra text, no explanation, just JSON
- Match part names from the inventory list above (case insensitive)
- If part is not found return action: "not_found"
- If command is unclear return action: "unclear"

JSON format for each action:

For adding stock:
{{"action": "add_stock", "part_id": 1, "part_name": "Engine Oil", "quantity": 10, "message": "Adding 10 units to Engine Oil"}}

For reducing stock:
{{"action": "reduce_stock", "part_id": 1, "part_name": "Engine Oil", "quantity": 5, "message": "Reducing Engine Oil stock by 5 units"}}

For setting exact stock:
{{"action": "set_stock", "part_id": 1, "part_name": "Engine Oil", "quantity": 20, "message": "Setting Engine Oil stock to 20 units"}}

For updating price:
{{"action": "update_price", "part_id": 1, "part_name": "Engine Oil", "price": 500, "message": "Updating Engine Oil price to Rs 500"}}

For setting minimum stock:
{{"action": "set_min_stock", "part_id": 1, "part_name": "Engine Oil", "quantity": 5, "message": "Setting minimum stock of Engine Oil to 5"}}

For checking stock:
{{"action": "check_stock", "part_name": "Engine Oil", "message": "Checking stock information"}}

For not found:
{{"action": "not_found", "message": "Part not found in inventory"}}

For unclear command:
{{"action": "unclear", "message": "Could not understand the command"}}
"""

    try:
        response = client.chat.completions.create(
            model    = "llama-3.3-70b-versatile",
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": command}
            ],
            max_tokens  = 200,
            temperature = 0.1
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace('```json', '').replace('```', '').strip()
        result = json.loads(raw)
        return result

    except json.JSONDecodeError:
        return {
            "action"  : "unclear",
            "message" : "Could not understand the command. Please try again."
        }
    except Exception as e:
        return {
            "action"  : "error",
            "message" : f"Error: {str(e)}"
        }


def execute_inventory_command(result, original_command):
    from app.models import SparePart, InventoryLog
    from app import db

    action = result.get('action')

    def save_log(part_name, action, quantity=None,
                 old_value=None, new_value=None, part_id=None):
        log = InventoryLog(
            part_id   = part_id,
            part_name = part_name,
            action    = action,
            quantity  = quantity,
            old_value = old_value,
            new_value = new_value,
            command   = original_command
        )
        db.session.add(log)
        db.session.commit()

    if action == 'add_stock':
        part = SparePart.query.get(result['part_id'])
        if part:
            old_stock  = part.stock
            part.stock += int(result['quantity'])
            db.session.commit()
            save_log(
                part_name = part.name,
                action    = 'Stock Added',
                quantity  = int(result['quantity']),
                old_value = old_stock,
                new_value = part.stock,
                part_id   = part.id
            )
            return {
                "success" : True,
                "message" : f"Successfully added {result['quantity']} units to {part.name}. Stock updated from {old_stock} to {part.stock}."
            }

    elif action == 'reduce_stock':
        part = SparePart.query.get(result['part_id'])
        if part:
            qty = int(result['quantity'])
            if part.stock < qty:
                return {
                    "success" : False,
                    "message" : f"Cannot reduce! Current stock of {part.name} is only {part.stock} units."
                }
            old_stock  = part.stock
            part.stock -= qty
            db.session.commit()
            save_log(
                part_name = part.name,
                action    = 'Stock Reduced',
                quantity  = qty,
                old_value = old_stock,
                new_value = part.stock,
                part_id   = part.id
            )
            return {
                "success" : True,
                "message" : f"Successfully reduced {part.name} stock from {old_stock} to {part.stock}."
            }

    elif action == 'set_stock':
        part = SparePart.query.get(result['part_id'])
        if part:
            old_stock  = part.stock
            part.stock = int(result['quantity'])
            db.session.commit()
            save_log(
                part_name = part.name,
                action    = 'Stock Set',
                quantity  = int(result['quantity']),
                old_value = old_stock,
                new_value = part.stock,
                part_id   = part.id
            )
            return {
                "success" : True,
                "message" : f"Successfully set {part.name} stock from {old_stock} to {part.stock}."
            }

    elif action == 'update_price':
        part = SparePart.query.get(result['part_id'])
        if part:
            old_price  = part.price
            part.price = float(result['price'])
            db.session.commit()
            save_log(
                part_name = part.name,
                action    = 'Price Updated',
                old_value = old_price,
                new_value = part.price,
                part_id   = part.id
            )
            return {
                "success" : True,
                "message" : f"Successfully updated {part.name} price from Rs {old_price} to Rs {part.price}."
            }

    elif action == 'set_min_stock':
        part = SparePart.query.get(result['part_id'])
        if part:
            old_min    = part.min_stock
            part.min_stock = int(result['quantity'])
            db.session.commit()
            save_log(
                part_name = part.name,
                action    = 'Min Stock Set',
                quantity  = int(result['quantity']),
                old_value = old_min,
                new_value = part.min_stock,
                part_id   = part.id
            )
            return {
                "success" : True,
                "message" : f"Successfully set minimum stock of {part.name} to {part.min_stock} units."
            }

    elif action == 'check_stock':
        parts = SparePart.query.filter(
            SparePart.name.ilike(f"%{result['part_name']}%")
        ).all()
        if parts:
            info = "\n".join([
                f"{p.name}: {p.stock} units in stock (Min: {p.min_stock}) | Price: Rs {p.price}"
                for p in parts
            ])
            return {"success": True, "message": info}
        return {
            "success" : False,
            "message" : f"Part not found: {result['part_name']}"
        }

    elif action == 'not_found':
        return {
            "success" : False,
            "message" : result.get('message', 'Part not found in inventory!')
        }

    elif action == 'unclear':
        return {
            "success" : False,
            "message" : result.get('message', 'Command not clear. Please try again.')
        }

    return {
        "success" : False,
        "message" : "Could not process command."
    }