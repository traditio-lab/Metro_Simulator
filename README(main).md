Delhi Metro Simulator - README


--> datetime module is used
--> The consecutive average travel time between stations is mostly assumed to be 2 or 3 mins for simplicity.
--> An interchange delay of 4 minutes is assumed.

--> ChatGPT , Github Copilot and Youtube Tutorials used for debugging and suggestions.
--> Sources : Wikipedia and official DMRC website


--> For bonus , a fare calculator is added in the Ride Journey Planner which calculates fare at Rupees 11 per station , for all cases
--> Breadth First Search is used to find the shortest possible route based on fewest stations , since travel time between stations is almost always 2 or 3 minutes 
    The route with fewer stations is  ALWAYS going to be faster when each step has almost the same weight.
--> Time should be input in 24 hour format in order for the program to function properly

-->  There could be cases where BFS would lead to more time , however since our program only deals with blue and magenta lines , so there is no exceptional case.

--> In journey planner , it shows each station name in between journey in the output.

--> To run the simulation , run the program and simply input 1 ,2 or 3 as per the functionality you wish to utilise.
--> The simulation keeps running in an infinite while loop unless you exit (press 3)
--> Graphs and Queues are used along with BFS  for route planning(shortest hop path)
--> Almost all exceptions are handled carefully , so the program should not be throwing an error in most cases.

# Program is run from the terminal
# Sample Test Cases

<!-- '''Line(Blue or Magenta) = Blue
Station = Yamuna Bank
Current time(24 hour format) = 1:20
No service available''' -->

<!-- 
Line(Blue or Magenta) = Blue
Station = Yamuna Bank
Current time(24 hour format) = 1:20
No service available

Choose functionality :
1 - Metro Timings Module
2 - Ride Journey Planner (with fare calculation)
3 - Exit Program
Enter choice :  2
Source: IIT
Destination: Yamuna Bank
Time of travel(in 24 hour format ie HH:MM): 12:00

Journey Plan:
Start at IIT (Magenta)
Next metro at 12:00
Arrive at Hauz Khas at 12:03
Arrive at Panchsheel Park at 12:06
Arrive at Chirag Delhi at 12:09
Arrive at Greater Kailash at 12:12
Arrive at Nehru Enclave at 12:15
Arrive at Kalkaji Mandir at 12:18
Arrive at Okhla NSIC at 12:21
Arrive at Sukhdev Vihar at 12:24
Arrive at Jamia Millia Islamia at 12:27
Arrive at Okhla Vihar at 12:30
Arrive at Jasola Vihar Shaheen Bagh at 12:33
Arrive at Kalindi Kunj at 12:36
Arrive at Okhla Bird Sanctuary at 12:39
Arrive at Botanical Garden at 12:42
Transfer to Blue
Next Blue metro departs at 12:48
Arrive at Noida Sector 18 at 12:51
Arrive at Noida Sector 16 at 12:54
Arrive at Noida Sector 15 at 12:57
Arrive at New Ashok Nagar at 13:00
Arrive at Mayur Vihar Extension at 13:03
Arrive at Mayur Vihar I at 13:06
Arrive at Akshardham at 13:09
Arrive at Yamuna Bank at 13:12
Final arrival at 13:12
Total travel time: 72 minutes
Total fare for your Journey : Rupees 242. -->



Name : Dishank Ramawat
Roll No 2025193
Sec A IP Group 9



