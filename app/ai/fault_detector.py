FAULT_DATABASE = {
    "noise while braking": {
        "issues": ["Brake pads worn out", "Brake disc damaged", "Loose brake caliper"],
        "action": "Inspect and replace brake pads. Check brake disc for wear.",
        "urgency": "high"
    },
    "bike not starting": {
        "issues": ["Dead battery", "Faulty spark plug", "Fuel supply issue"],
        "action": "Check battery voltage, inspect spark plug, check fuel level.",
        "urgency": "high"
    },
    "engine overheating": {
        "issues": ["Low engine oil", "Coolant leak", "Blocked air filter"],
        "action": "Check oil level, inspect coolant, clean or replace air filter.",
        "urgency": "high"
    },
    "bike vibrating": {
        "issues": ["Unbalanced tyres", "Loose engine bolts", "Worn suspension"],
        "action": "Balance tyres, tighten engine bolts, inspect suspension.",
        "urgency": "medium"
    },
    "poor mileage": {
        "issues": ["Dirty air filter", "Old spark plug", "Tyre pressure low"],
        "action": "Replace air filter, change spark plug, inflate tyres.",
        "urgency": "low"
    },
    "chain noise": {
        "issues": ["Chain too loose", "Chain needs lubrication", "Worn sprocket"],
        "action": "Adjust chain tension, lubricate chain, inspect sprocket.",
        "urgency": "medium"
    },
    "smoke from engine": {
        "issues": ["Oil burning", "Coolant leak into engine", "Piston ring worn"],
        "action": "Check oil level, inspect head gasket, visit mechanic immediately.",
        "urgency": "high"
    },
    "headlight not working": {
        "issues": ["Blown bulb", "Faulty wiring", "Dead battery"],
        "action": "Replace bulb, check wiring connections, test battery.",
        "urgency": "medium"
    },
    "gear shifting problem": {
        "issues": ["Clutch cable loose", "Gear oil low", "Bent gear lever"],
        "action": "Adjust clutch cable, top up gear oil, inspect gear lever.",
        "urgency": "medium"
    },
    "tyre puncture": {
        "issues": ["Nail or sharp object in tyre", "Valve stem leak", "Tyre worn out"],
        "action": "Repair or replace tyre, check valve stem, inspect tyre condition.",
        "urgency": "high"
    }
}


def detect_fault(problem_description):
    problem = problem_description.lower().strip()

    for keyword, data in FAULT_DATABASE.items():
        if any(word in problem for word in keyword.split()):
            return {
                "matched"  : True,
                "keyword"  : keyword,
                "issues"   : data["issues"],
                "action"   : data["action"],
                "urgency"  : data["urgency"]
            }

    return {
        "matched": False,
        "issues" : ["Could not identify issue from description"],
        "action" : "Please visit the garage for a physical inspection.",
        "urgency": "unknown"
    }