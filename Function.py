from random import randint

on_going_events = []

def start_event(start_time, event_owner,event_id=randint(100,999)): #create the event

  check = [events[id] for events in on_going_events] # all ids in use

  while event_id in check: 
    event_id = randint(100,999)
  participants = {event_info:[event_id,0], event_owner:start_time} # assign a unique id to the event and creates the list of participants


def joining(name, start_time, event_id): # join a on going event
  for event in on_going_events: # loops through all current events
    if event[event_info[0]] == event_id:
      if name not in event: # adds new participant if not already present in the event
        event[name:start_time]
        break # stops the loop after adding(no need to go through everything)

# def leaving(name, event_id):
#   for event in on_going_events:
#     if event[event_info[0]] == event_id:
#     if name in 


def percentages(event_id): # calculates Percentages based on time spent on the event
  participant = event.items()

  loot = participant[0[0[0]]]
  perc = {event_info:[event_id,loot]}
  participant.pop(0)
  start_time = participant[0[0]]

  for p in participant: # p é uma lista no formato [nome,tempo]
    perc[p[0]:round(p[1]/start_time,2)]

  return perc


def add_loot(amount,event_id):
  for event in on_going_events:
    if event[event_info[0]] == event_id:
      event[event_info[1]] += amount
      break

def sub_loot(amount,event_id):
  for event in on_going_events:
    if event[event_info[0]] == event_id:
      event[event_info[1]] -= amount
      break

def end_event(event_id):
  for event in on_going_events:
    if event[event_info[0]] == event_id:

      perc = percentages(event_id)
      n_participants = range(perc[1:])
      even_split = round(1/n_participants,2)
      full_participation = []
      event_end = {event_info[event_id,event_info[1]]}
      rest = 0

      for person in perc[1:]:
        if person[1] == 1:
          full_participation.append(person[0])
          event_end[person[0],event[event_info[1]*even_split]
        else:
          split = even_split*person[1]
          event_end[person[0],event[event_info[1]*split]
          rest += 1-split
    break
    return event_end
