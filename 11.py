import mysql.connector as mq
con=mq.connect(host = "localhost", user="root",password="root",database="db1")
cur=con.cursor()
a=int(input("Enter Roll Number : "))
b=input("Enter Name : ")
c=int(input("Enter Percentage : "))
query="insert into student values(%s,%s,%s)"
data=(a,b,c)
cur.execute(query,data)
con.commit()
con.close()
