import json
from datetime import datetime


def get_time():
    time = datetime.utcnow().time()
    return [time.hour, time.minute, time.second]

def time_passed(t,t2=get_time()):
    time = list(map(lambda x, y: y - x, t2, t))
    return sum([time[0] * 3600 + time[1] * 60 + time[2]])


def joining(name, event_id, initial_time=get_time()):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
        ctx_event = event_list[event_id]
        names = [i["name"] for i in ctx_event["participants"]]
        if name not in names:
            ctx_event["participants"].append({"name": name, "start_time": initial_time, "end_time": None, "loot": 0})
            event_list[event_id] = ctx_event
            file.seek(0)
            json.dump(event_list, file, indent=4)
        else:
            pass  # add bot msg?


def leaving(name, event_id, leaving_time=get_time()):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
        ctx_event = event_list[event_id]
        names = [i["name"] for i in ctx_event["participants"]]
        if name in names:
            i = names.index(name)
            ctx_event["participants"][i]["end_time"] = leaving_time
            event_list[event_id] = ctx_event
            file.seek(0)
            json.dump(event_list, file, indent=4)
        else:
            pass  # add bot msg?


def event_start(owner, id, guild, start=get_time()):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
        event_list[id] = {"guild": guild.id, "creator": owner, "start": start, "loot": 0, "participants": []}
        file.seek(0)
        json.dump(event_list, file, indent=4)


def split(event_id):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
        ctx_event = event_list[event_id]
        loot = ctx_event["loot"]
        participants = ctx_event["participants"]
        total_time = 0
        for p in participants:
            total_time += time_passed(p["end_time"], p["start_time"])
        loot_per_time = loot / total_time
        for p in participants:
            p["loot"] = time_passed(p["end_time"], p["start_time"]) * loot_per_time
        event_list[event_id] = ctx_event
        file.seek(0)
        json.dump(event_list, file, indent=4)


def end_event(event_id, end_time=get_time()):
    with open("event_list.json", "r+") as file:
        event_list = json.load(file)
        ctx_event = event_list[event_id]
        participants = ctx_event["participants"]
        for person in participants:
            leaving(person["name"], event_id)
        split(event_id)
