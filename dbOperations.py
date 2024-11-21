import sqlite3
connection = sqlite3.connect("studentDB.db")
cursor = connection.cursor()

cursor.execute("SELECT * FROM studentCredential")
print(cursor.fetchall())

'''cursor.execute("""CREATE TABLE studentCertification(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email text not null,
                name text not null,
                platform text not null,
                certificationType text not null,
                particulars text not null,
                freePaid text not null,
                mode text not null,
                year text not null,
                section text not null,
                semester text not null,
                courseType text not null,
                duration text not null,
                fromDate text not null,
                toDate text not null,
                fileName text not null,
                certificate BLOB
                )""")'''

'''cursor.execute("""CREATE TABLE studentActivities(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email text not null,
                    specificEvent text not null,
                    eventName text not null,
                    eventDate text not null,
                    location text not null,
                    collegeName text not null,
                    price text not null,
                    cashPrize text not null,
                    additionalInfo text not null,
                    fileName text not null,
                    certificate BLOB);""")'''

'''cursor.execute("""CREATE TABLE studentCredential(
                    rollNumber text not null primary key,
                    firstName text not null,
                    lastName text not null,
                    mailID text not null unique,
                    dept text not null,
                    section text not null,
                    phoneNumber int not null,
                    password text not null,
                    imageName TEXT not null,
                    image BLOB,
                    dob text not null,
                    address text not null)""")'''
    


'''stmt = "INSERT INTO studentCredential VALUES (?,?,?,?,?,?,?,?);" 
cursor.execute(stmt,('23ITR113','Nitish','M','nitishm.23it@kongu.edu','Information Technology','B',8675851166,'Nitish@123'))
connection.commit()'''

