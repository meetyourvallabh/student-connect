# Program to display the Fibonacci sequence up to n-th term
nterms = int(input("How many terms? "))

# first two terms
n1, n2 = 0, 1


# check if the number of terms is valid
if nterms <= 0:
    print("Please enter a positive integer")
elif nterms == 1:
    print("Fibonacci sequence upto",nterms,":")
    print(n1)
else:
    print("Fibonacci sequence:")
    for i in range(0,nterms):
       print(n1,end =" ")  #using end=" " for printing all numbers on same line with whitespace
       sum = n1 + n2      #adding previous number and latest number
       
       n1 = n2    # updating previous number
       n2 = sum   # updating latest number


    print()



    