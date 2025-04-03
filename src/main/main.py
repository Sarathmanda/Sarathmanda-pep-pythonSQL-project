import csv
import re
import sqlite3

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users('../../resources/users.csv')
    load_and_clean_call_logs('../../resources/callLogs.csv')
    write_user_analytics('../../resources/userAnalytics.csv')
    write_ordered_calls('../../resources/orderedCalls.csv')

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    with open(file_path,'r') as file:
        reader=csv.reader(file)
        next(reader)

        for row in reader:
            if len(row)<2 or len(row)>3:
                continue
            first_name=row[0].strip()
            last_name=row[1].strip()

            if not first_name or not last_name:
                continue

            if re.fullmatch(r'#+', last_name) and len(row)==3 and row[2].strip():
                last_name=row[2].strip()
            
            if not last_name or last_name=="####":
                continue
            cursor.execute('''INSERT INTO users(firstName,lastName) VALUES(?,?)''',(first_name,last_name))
    conn.commit()

    print("TODO: load_users")


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    with open(file_path,'r') as file:
        reader=csv.reader(file)
        headers=next(reader)

        expected_columns=5

        for row in reader:
            if len(row)!=expected_columns or "" in row:
                continue
            phone_number,start_time,end_time,direction,user_id=row
            try:
                start_time=int(float(start_time))
                end_time=int(float(end_time))
                user_id=int(user_id)

                cursor.execute(''' INSERT INTO callLogs(phoneNumber,startTime,endTime,direction,userId) VALUES (?,?,?,?,?)''',(phone_number,start_time,end_time,direction,user_id))
            except ValueError:
                continue
    conn.commit()

    print("TODO: load_call_logs")


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):

    cursor.execute('''SELECT userId,SUM(endTime-startTime) AS totalDuration, COUNT(*) AS numCalls
    FROM callLogs
    GROUP BY userId''')

    user_analytics=[]

    for row in cursor.fetchall():
        user_id,total_duration,num_calls=row
        avg_duration=total_duration/num_calls if num_calls > 0 else 0
        user_analytics.append((user_id,avg_duration,num_calls))

    with open(csv_file_path,'w',newline='',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow(["userId","avgDuration","numCalls"])
        writer.writerows(user_analytics)

    print("TODO: write_user_analytics")


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):

    cursor.execute(''' SELECT callId,phoneNumber,startTime,endTime,direction,userId
    FROM callLogs''')

    call_logs=cursor.fetchall()

    if not call_logs:
        print("No call logs found.Ensure data is loaded before running this function.")
        return

    sorted_call_logs=sorted(call_logs,key=lambda x: (x[5], x[2]))

    with open(csv_file_path,'w',newline='',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow(["callId","phoneNumber","startTime","endTime","direction","userId"])
        writer.writerows(sorted_call_logs)

    print("TODO: write_ordered_calls")



# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()
