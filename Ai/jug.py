def waterjug():

    a=0
    b=0
    print("A=",a,"B=",b)

    b=5
    print("A=",a,"B=",b)

    transfer=min(b,3-a)
    b=b-transfer
    a=a+transfer
    print("A=",a,"B=",b)

    a=0
    print("A=",a,"B=",b)
    
    transfer=min(b,3-a)
    b=b-transfer
    a=a+transfer
    print("A=",a,"B=",b)

    b=5
    print("A=",a,"B=",b)
     
    transfer=min(b,3-a)
    b=b-transfer
    a=a+transfer
    print("A=",a,"B=",b)

    print("A=",a,"B=",b)
    if (a == 4 ) or (b== 4):
       print("we achived")
waterjug()
