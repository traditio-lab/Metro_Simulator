# reads data from metro_data.txt and provides ride journey planner and metro timings module
 
from datetime import datetime, timedelta 
from collections import deque

data_file = "metro_data.txt"

interchange_delay = 4 # interchange delay of 4 minutes taken

# parsing data from  metro_data.txt

def load_data():
    '''
    Loads graph and station-lines mapping from the text file by building two data structures.      
    '''
    graph = {}     # tells which connects to what , travel time and metro line.
    station_lines = {}  # mapping of each station to its metro lines, either blue or magenta or both
    with open(data_file, "r") as f:
        for data in f:
            lines = data.strip()
            if not lines or lines.startswith("#"):  # skip blank lines or any lines starting with # (ie comments) in text file
                continue
            info = [i.strip() for i in lines.split(",")]
            if len(info) < 5:  # skip any incomplete or malformed lines
                continue
            line, station, next_station, t_min, interchange = info # parsing and mapping the data of text file
            try:
                t_min = int(t_min)  #  type cast travel time  to a integer 
            except:
                t_min = 3 # elif there is error , assume a default of 3 minutes.

             # we need to add connections from both sides since metro network is bi directional   
            graph.setdefault(station, []).append((next_station, t_min, line))
            graph.setdefault(next_station, []).append((station, t_min, line))
            
            station_lines.setdefault(station, set()).add(line)
            station_lines.setdefault(next_station, set()).add(line)
            
    return graph, station_lines


'''if the file contains , for example:

Blue,Dwarka Sector 21,Dwarka Sector 8,2,No
Blue,Dwarka Sector 8,Dwarka Sector 9,2,No
Blue,Dwarka Sector 9,Dwarka Sector 10,2,No

graph becomes :
{
  "Dwarka Sector 21": [("Dwarka Sector 8", 2, "Blue")],
  "Dwarka Sector 8": [("Dwarka Sector 21", 2, "Blue"), ("Dwarka Sector 9", 2, "Blue")],
  "Dwarka Sector 9": [("Dwarka Sector 8", 2, "Blue"), ("Dwarka Sector 10", 2, "Blue")] ,
  "Dwarka Sector 10": [("Dwarka Sector 9" , 2 , "Blue")]
  }

  
station_lines becomes:
{
"Dwarka Sector 21" :{"Blue"} ,
"Dwarka Sector 8" : {"Blue"} ,
"Dwarka Sector 9" : {"Blue"} ,
"Dwarka Sector 10" : {"Blue"} ,


}

'''       


def return_time_24hour(s):
    return datetime.strptime(s.strip(), "%H:%M").time()   # returns a time string of 24 hour format using datetime module(parsing time)

def in_service(t):
    return return_time_24hour("06:00") <= t <= return_time_24hour("23:00") # checks whether current time falls under service hours or not

def frequency_arrival(t):
    
    # calculates the train frequency in minutes at a given time(in 24 hour format)
    '''for peak timings 8 am to 10 am and 5 pm to 7 pm , frequency of arrival is 4 mins ,else it is 8 mins'''
    
    if return_time_24hour("08:00") <= t < return_time_24hour("10:00"):  # 4 mins for peak hours , 8 am to 10 pm
        return 4  
    if return_time_24hour("17:00") <= t < return_time_24hour("19:00"): # also 5 pm to 7 pm
        return 4
    return 8   # 8 mins for non-peak hours  

def next_train_time(current_time):
    # computes the arrival time of train at , or after the current_time 
    start = datetime.combine(datetime.today(), return_time_24hour("06:00"))
    end = datetime.combine(datetime.today(), return_time_24hour("23:00"))
    now = datetime.combine(datetime.today(), current_time)
    if now < start or now > end:    
        return None  # no trains if current_time is outside the service hours.
    t = now
    while t <= end:
        m = (t - start).seconds // 60
        if m % frequency_arrival(t.time()) == 0:
            if t >= now:
                return t.time()
        t += timedelta(minutes=1)
    return None

def subsequent_trains(first_time, count=5):
    # compute the arrival time of subsequent trains 
    if first_time is None:
        return []
    res = []
    t = datetime.combine(datetime.today(), first_time)
    # ensure we don't generate trains after service end (23:00)
    service_end_dt = datetime.combine(datetime.today(), return_time_24hour("23:00"))
    for _ in range(count):
        t += timedelta(minutes=frequency_arrival(t.time()))
        if t > service_end_dt:
            break
        res.append(t.time().strftime("%H:%M"))
    return res


 # for finding the shortest path(fewest stations.) path between source and destination.
def bfs_path(graph, source, destination):   # breadth first search 
    if source == destination:  # if source and destination are same , it is simply that one station.
        return [source]
    q = deque([[source]])
    visited = set([source])    
    while q:
        path = q.popleft()
        node = path[-1]
        for neighbor, t_min, line in graph.get(node, []):
            if neighbor in visited:
                continue
            newpath = path + [neighbor]
            if neighbor == destination:
                return newpath
            visited.add(neighbor)
            q.append(newpath)
    return None

# -------------------------
# Compute schedule for a path
# -------------------------
def calculate_schedule(path, graph, boarding_time):
    # returns list of tuples: (station, time_str, tag)
    schedule = []
    dt = datetime.combine(datetime.today(), boarding_time)
    schedule.append((path[0], dt.time().strftime("%H:%M"), "Board"))
    service_end_dt = datetime.combine(datetime.today(), return_time_24hour("23:00"))
    for i in range(len(path)-1):
        s = path[i]; n = path[i+1]
        tmin = None
        for neighbor, t_min, line in graph.get(s, []):
            if neighbor == n:
                tmin = t_min 
                break
        if tmin is None: 
            tmin = 3
        dt += timedelta(minutes=tmin)
        # if this arrival is beyond service end, report and stop further scheduling
        if dt > service_end_dt:
            schedule.append((n, dt.time().strftime("%H:%M"), "Arrive (after service end)"))
            break
        schedule.append((n, dt.time().strftime("%H:%M"), "Arrive"))
    return schedule

# --------------------------------------------------------------- METRO TIMINGS MODULE ----------------------------------------- #


def find_station_match(graph, query):  # finds the station names if user does not input exact station name or does not care
    q = query.strip().lower()          # about lower case , upper case or prefixes 
    stations = list(graph.keys())
    # exact match
    for s in stations:
        if s.lower() == q:
            return s    # return the station name immediately 
    # startswith
    starts = [s for s in stations if s.lower().startswith(q)]  # checks for prefix , for eg if user types "bot" it will return "Botanical Garden" automatically avoiding any sort of errors.
    if len(starts) == 1:
        return starts[0]
    # substring matches
    subs = [s for s in stations if q in s.lower()]
    if len(subs) == 1:
        return subs[0]
    
    candidates = starts + subs  
    return candidates[:6]  # if the input for station name is still ambigous , return a list of suggestions.

def do_metro_timings(graph, station_lines):

    # takes user input for line , station and time. 
    
    line = input("Line(Blue or Magenta) = ").strip()
    station_input = input("Station = ").strip()
    time = input("Current time(24 hour format) = ").strip()

    
    station_match = find_station_match(graph, station_input)   # match station name robustly
    if isinstance(station_match, list): 
        if not station_match:   
            print("Station not found. Check spelling.")
            return
        print("Station ambiguous. Suggestions:", "; ".join(station_match))
        return
    station = station_match

    try:
        t = return_time_24hour(time)
    except:
        print("Invalid time format. Use HH:MM ie 24 hour format.")
        return
    if not in_service(t):
        print("No service available")
        return
    nxt = next_train_time(t)
    if nxt is None:
        print("No service available")
        return
    
    print(f"\nNext metro at {nxt.strftime('%H:%M')}")
    subs = subsequent_trains(nxt, 5)
    if subs:
        print("Subsequent metros at " + ", ".join(subs) + "....")
    else:
        print("No further trains...")

    



# ----------------------------------------- RIDE JOURNEY PLANNER --------------------------------------------- #        

def calculator_fare(path):   # calculating fare  at rupees 11 per station (bonus)
        if not path or len(path) < 2:
            return 0
        stations_travelled = len(path) - 1
        fare = stations_travelled * 11
        return fare

def do_journey_planner(graph, station_lines):  # Ride Journey Planner
    source_input = input("Source: ").strip()      # start station input
    destination_input = input("Destination: ").strip()  # end station input
    time = input("Time of travel(in 24 hour format ie HH:MM): ").strip()   # time of start  
    try:
        t = return_time_24hour(time)  # the input time is converted to a time object in HH:MM
    except:
        print("Invalid time format. Use 24 hour format")
        return  # if conversion errors , error is handled.
    if not in_service(t):    # checks availability of train in service hours.
        print("No service available")
        return  

    first_train = next_train_time(t)
    if first_train is None:
        print("No service available")
        
        return

    # robust station match
    src_match = find_station_match(graph, source_input)
    if isinstance(src_match, list):
        if not src_match:
            print("Source not found.")
            return
        print("Source ambiguous. Options:", "; ".join(src_match))
        return
    src = src_match


    # same logic for destination.
    dst_match = find_station_match(graph, destination_input)
    if isinstance(dst_match, list):
        if not dst_match:
            print("Destination not found.")
            return
        print("Destination ambiguous. Options:", "; ".join(dst_match))
        return
    dst = dst_match 

    path = bfs_path(graph, src, dst)   # uses BFS algorithm to find a route between the source and destination ,
    if not path:
        print("No feasible route between stations.")
        return  # if no route is found, the function is exited.

    schedule = calculate_schedule(path, graph, first_train)

    
    print("\nJourney Plan:")
   
    lines_source = station_lines.get(src, set())
    if lines_source:
        line_src = list(lines_source)[0]
    else:
        line_src = "Unknown Line"
    print(f"Start at {src} ({line_src})")
    print(f"Next metro at {first_train.strftime('%H:%M')}")

    # Print station-wise arrival times
    # Also detect interchange: when a station has more than one line available and the path later continues on a different line
    # We'll compute line used between consecutive stations to find where line changes happen
    used_lines = []
    for i in range(len(path)-1):
        s = path[i]; n = path[i+1]
        line_used = None
        for neighbor, t_min, line in graph.get(s, []):
            if neighbor == n:
                line_used = line 
                break
        used_lines.append(line_used)

   
    for idx, (st, tm, tag) in enumerate(schedule):
        if idx == 0:
          
            continue
        print(f"Arrive at {st} at {tm}")
       
        if idx < len(used_lines):
            # compare line used for previous and next segments if possible
            prev_line = used_lines[idx-1] if idx-1 < len(used_lines) else None
            next_line = used_lines[idx] if idx < len(used_lines) else None
            if prev_line and next_line and prev_line != next_line:
                # Transfer required here
                print(f"Transfer to {next_line}")
                # compute next train on connecting line based on arrival time
                arrival_dt = datetime.combine(datetime.today() , return_time_24hour(tm))
                arrival_dt+=timedelta(minutes= interchange_delay)
                arrival_time = arrival_dt.time()
                nxt_connecting_train_time = next_train_time(arrival_time)
                
                if nxt_connecting_train_time:
                    print(f"Next {next_line} metro departs at {nxt_connecting_train_time.strftime('%H:%M')}")
                    
                    remaining_path = path[idx:]
                    new_schedule = calculate_schedule(remaining_path, graph, nxt_connecting_train_time)
                    
                    for st2, tm2, tag2 in new_schedule[1:]:
                        print(f"Arrive at {st2} at {tm2}")
                   
                    start_dt = datetime.combine(datetime.today(), first_train)
                    final_arrival = return_time_24hour(new_schedule[-1][1])
                    end_dt = datetime.combine(datetime.today(), final_arrival)
                    total_minutes = int((end_dt - start_dt).total_seconds() // 60)
                    print(f"Final arrival at {new_schedule[-1][1]}")
                    print(f"Total travel time: {total_minutes} minutes")
                    fare = calculator_fare(path)
                    print(f"Total fare for your Journey : Rupees {fare}.")
                    
                    
                    return

    final_arrival = schedule[-1][1]     
    start_dt = datetime.combine(datetime.today(), first_train)
    end_dt = datetime.combine(datetime.today(), return_time_24hour(final_arrival))   # in case there is no interchange , we directly calculate the journey plan.
    total_minutes = int((end_dt - start_dt).total_seconds() // 60)
    print(f"Final arrival at {final_arrival}")
    print(f"Total travel time: {total_minutes} minutes")
    
    fare = calculator_fare(path)
    print(f"Total fare for your Journey : Rupees {fare}.")


# Main Program

def main():
    graph, station_lines = load_data()

    while True:               # allows user to choose either of the functionalities.
        print("\nChoose functionality : ")
        print("1 - Metro Timings Module")
        print("2 - Ride Journey Planner (with fare calculation)")
        print("3 - Exit Program")
        
        c = input("Enter choice :  ").strip()
        if c == "1":
            do_metro_timings(graph, station_lines)  # calls the metro timings function             
        elif c == "2":
            do_journey_planner(graph, station_lines) # calls jounret planner function
        elif c == "3":
            print("Simulation Ended !")
            break                      # 3- program ends , loop breaks
        else:
            print("Invalid choice")  # invalid choice - loop continues until valid input is given


    
main()  
 





