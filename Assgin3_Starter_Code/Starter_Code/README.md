# How to use
In two seperate windows run Receiver.py followed by Sender.py. Specify what file you want to send by given its name along with extension like, test.txt
, and both will begin to print out that they are sending pack x and receiving packet x. Furthermore, Receiver.py will be filling in receiver_file_16.txt. 


# Bugs
Due to the probability of losing the packets the program can randomly stop and get stuck in an infinite loop due to the global done var, we belive that to
be the cause of the issue. Furthermore, we did not use two threads to implement the solution, rather it only used 1. Also, locking for threads was not applied 
either as neither of us seemed to be using it correctly. 
