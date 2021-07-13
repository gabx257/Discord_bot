import json
from datetime import datetime


def get_time():
    time = datetime.utcnow().time()
    return [time.hour, time.minute, time.second]

def time_passed(t):
    t2 = get_time()
    time = list(map(lambda x, y: (x - y), t2, t))
    return sum([time[0] * 3600 + time[1] * 60 + time[2]])


def joining(name, event_id):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
    ctx_event = event_list[event_id]
    names = [i["name"] for i in ctx_event["participants"]]
    if name not in names:
        ctx_event["participants"].append({"name": name, "start_time": get_time(), "spent_time": 0, "loot": 0})
        event_list[event_id] = ctx_event
    else:
        i = names.index(name)
        ctx_event["participants"][i]["start_time"] = get_time()
    with open("event_list.json", "w") as file:
        json.dump(event_list, file, indent=4)


def leaving(name, event_id):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
    ctx_event = event_list[event_id]
    names = [i["name"] for i in ctx_event["participants"]]
    if name in names:
        i = names.index(name)
        ctx_event["participants"][i]["spent_time"] += time_passed(ctx_event["participants"][i]["start_time"])
        event_list[event_id] = ctx_event
    with open("event_list.json", "w") as file:
            json.dump(event_list, file, indent=4)


def event_start(owner, id, guild, start=get_time()):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
    event_list[id] = {"guild": guild.id, "creator": owner, "start": start, "loot": 0, "participants": []}
    with open("event_list.json", "w") as file:
        json.dump(event_list, file, indent=4)


def split(event_id):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
    ctx_event = event_list[event_id]
    loot = ctx_event["loot"]
    participants = ctx_event["participants"]
    total_time = 0
    for p in participants:
        total_time += p["spent_time"]
    if total_time == 0:
        total_time = 1
    loot_per_time = loot / total_time
    for p in participants:
        p["loot"] = p["spent_time"] * loot_per_time
    event_list[event_id] = ctx_event
    with open("event_list.json", "w") as file:
        json.dump(event_list, file, indent=4)


def end_event(event_id, list_now):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
        ctx_event = event_list[event_id]
        participants = ctx_event["participants"]
        for person in participants:
            if person["name"] in list_now:
                leaving(person["name"], event_id)
        split(event_id)
        #create msg with the loot for each plyaer/ if msg was deleted, delete the event from event list

def add_loot(event_id, amount):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
    ctx_event = event_list[event_id]
    ctx_event["loot"] += amount
    with open("event_list.json", "r+") as file:
        json.dump(event_list,file,indent=4)


def sub_loot(event_id, amount):
    with open("event_list.json", "r") as file:
      event_list = json.load(file)
    ctx_event = event_list[event_id]
    ctx_event["loot"] -= amount
    with open("event_list.json", "w") as file:
        json.dump(event_list,file,indent=4)

def loot_list(event_id):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
    ctx_event = event_list[event_id]
    total_loot = ctx_event["loot"]
    duration = time_passed(ctx_event["start"])
    list = {p["name"]: p["loot"] for p in ctx_event["participants"]}
    return [total_loot, duration, list]


def delete_event(id):
    with open("event_list.json", "r") as file:
        event_list = json.load(file)
    del event_list[id]
    with open("event_list.json", "w") as file:
        json.dump(event_list, file, indent=4)
