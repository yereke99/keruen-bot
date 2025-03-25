from sqlite3 import connect
from xlsxwriter.workbook import Workbook
import random
from datetime import datetime

class Database():
    def __init__(self) -> None:
        self.db = connect('./keruen.db')
        self.cursor = self.db.cursor()

        self.counter = """
                        CREATE TABLE statistics(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tik_tok BIGINT,
                            instagram BIGINT
                        )
                       """

        self.tableMoney = """CREATE TABLE money(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    sum BIGINT
                                )"""


        self.tableJustClicked = """CREATE TABLE just(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    id_user BIGINT,
                                    userName VARCHAR(255),
                                    dataRegistred VARCHAR(255)
                                )"""

        self.tableCreate =  """CREATE TABLE client(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    id_user BIGINT,
                                    userName VARCHAR(255), 
                                    fio VARCHAR(255),
                                    contact VARCHAR(255),
                                    city VARCHAR(255),
                                    dateRegister VARCHAR(255),
                                    dataPay VARCHAR(255),
                                    checks BOOLEAN
                            )"""
        
        self.tableLoto  =     """CREATE TABLE loto(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    id_user BIGINT,
                                    id_loto INTEGER,
                                    qr VARCHAR(255),
                                    who_paid VARCHAR(255),
                                    receipt VARCHAR(255),
                                    fio VARCHAR(255),
                                    contact VARCHAR(255),
                                    city VARCHAR(255),
                                    dataPay VARCHAR(255)
                                )"""
        
        self.tableCinema =  """CREATE TABLE cinemaLoto(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    loto INTEGER,
                                    checks BOOLEAN
                            )"""

        
        self.tableCinemaPaid = """CREATE TABLE cinema(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    id_user BIGINT,
                                    movId VARCHAR(5000),
                                    dataPaid VARCHAR(255)
                                )"""
        

        self.justInsert =   """INSERT INTO just(
                                    id_user,
                                    userName,
                                    dataRegistred
                            )VALUES(?,?,?)
                            """
        
        self.CinemaPaidInsert =   """INSERT INTO cinema(
                                    id_user,
                                    movId,
                                    dataRegistred
                            )VALUES(?,?,?)
                            """

        
        self.insertClient = """INSERT INTO client(
                                    id_user,
                                    userName,
                                    contact,
                                    dateRegister,
                                    dataPay,
                                    checks
                            )VALUES(?,?,?,?,?,?)
                            """

    def createTables(self):
        self.cursor.execute(self.tableCreate)
        self.cursor.execute(self.tableLoto)
        self.cursor.execute(self.tableJustClicked)
        self.cursor.execute(self.tableCinemaPaid)
        self.cursor.execute(self.tableMoney)
        self.cursor.execute(self.tableCinema)
        self.cursor.execute(self.counter)
        self.cursor.execute("INSERT OR IGNORE INTO money(id, sum) VALUES (1, 0)")
        self.cursor.execute("INSERT OR IGNORE INTO statistics(id, tik_tok, instagram) VALUES(1, 0, 0)")
    
        self.db.commit()
        print("Created all tables and initialized money table if necessary.")
    
    def get_receipt_by_id(self, id_loto: int) -> str:
        """Получает значение receipt по заданному id_loto из базы данных."""
        self.cursor.execute("SELECT receipt FROM loto WHERE id_loto = ?", (id_loto,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def tiktok_counter(self):
        # Инкрементируем значение tik_tok на 1
        self.cursor.execute("UPDATE statistics SET tik_tok = tik_tok + 1 WHERE id = 1")
        self.db.commit()

    def instagram_counter(self):
        # Инкрементируем значение instagram на 1
        self.cursor.execute("UPDATE statistics SET instagram = instagram + 1 WHERE id = 1")
        self.db.commit()

    def get_tiktok_count(self):
        # Получаем значение TikTok
        self.cursor.execute("SELECT tik_tok FROM statistics WHERE id = 1")
        return self.cursor.fetchone()[0]

    def get_instagram_count(self):
        # Получаем значение Instagram
        self.cursor.execute("SELECT instagram FROM statistics WHERE id = 1")
        return self.cursor.fetchone()[0]

    def JustInsert(self, id, userName, dataR) -> bool:
        try:
            if self.CheckUser(id) == False:
                self.cursor.execute(self.justInsert, (id, userName, dataR, ))
                self.db.commit()
                return True
        except Exception as e:
            print(e)
            return False    
        
    def InsertLoto(self, id_user, id_loto, qr, who_paid, receipt, fio, contact, city, dataPay) -> bool:
        try:
            insertLotoQuery = """INSERT INTO loto(
                                    id_user,
                                    id_loto,
                                    qr,
                                    who_paid,
                                    receipt,
                                    fio,
                                    contact,
                                    city,
                                    dataPay
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(insertLotoQuery, (id_user, id_loto, qr, who_paid, receipt, fio, contact, city, dataPay))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    
    def CheckLoto(self, qr: str) -> bool:
        print(qr)
        try:
            q = "SELECT COUNT(*) from loto WHERE  qr = ?"
            self.cursor.execute(q, (qr, ))
            count = self.cursor.fetchone()[0]
            print(count)
            return count > 0
        except Exception as e:
            print(e)
            return False
    
    def FetchIdLotoByUser(self, id_user: int) -> list:
        try:
            fetchQuery = "SELECT id_loto FROM loto WHERE id_user = ?"
            self.cursor.execute(fetchQuery, (id_user,))
            results = self.cursor.fetchall()
            return [row[0] for row in results]
        except Exception as e:
            print(e)
            return []


    def InsertClient(self, id, userName, fio, contact, city, dataR, dataP, check) -> bool:
        try:
            insertClientQuery = """INSERT INTO client(
                                    id_user,
                                    userName,
                                    fio,
                                    contact,
                                    city,
                                    dateRegister,
                                    dataPay,
                                    checks
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(insertClientQuery, (id, userName, fio, contact, city, dataR, dataP, check))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False


        
    def InsertPaid(self, id, movId, dataPaid) -> bool:
        try:
            self.cursor.execute(self.CinemaPaidInsert, (id, movId, dataPaid, ))
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False 

    def gatherJustID(self):
        
        self.cursor.execute("select id_user from just")
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
        

    def gather(self):
        self.cursor.execute("SELECT id_user FROM client")
        # Ensure that you're getting a list of integers
        idx = [int(id[0]) for id in self.cursor.fetchall()]
        return idx
        
    def gatherNotPaid(self):
        
        self.cursor.execute("select id_user from client where checks=?", ("false", ))
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
    
    def gatherPaid(self):
        
        self.cursor.execute("select id_user from client where checks=?", ("true", ))
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
    
    def gather4User(self, id):

        self.cursor.execute("Select userName,  contact, dateRegister, dataPay, checks WHERE id_user=?", (id, ))
        resultdata = [[i[0], i[1], i[2], i[3], i[4], i[5]] for i in self.cursor.fetchall()]

        return resultdata
    
    def gatherPayedForAdmin(self):
        self.cursor.execute("select id_user from client where checks=?", ("true", ))
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
    

    def gatherNotPayedForAdmin(self):
        self.cursor.execute("select id_user from client where checks=?", ("false", ))
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
    

    def CheckUser(self, id: int) -> bool:
        listOfId = self.gatherJustID()

        if id in listOfId:
            return True

        return False   
    
    
    def CheckUserNotPaid(self, id: int) -> bool:
        listOfId = self.gatherNotPaid()

        if id in listOfId:
            return True

        return False 
    
    def CheckUserPaid(self, id: int) -> bool:
        listOfId = self.gatherPaid()

        if id in listOfId:
            return True

        return False 
    
    def gatherC(self):
        
        self.cursor.execute("select id_user from client")
        idx = [int(''.join(map(str, id))) for id in self.cursor.fetchall()]
        
        return idx
    
    def CheckClickPaid(self, id: int) -> bool:
        listOfId = self.gatherC()

        if id in listOfId:
            return True

        return False 
    
  
    def gatherJust(self):
        self.cursor.execute("SELECT * FROM just")
        return self.cursor.fetchall()

    def gatherClients(self):
        self.cursor.execute("SELECT id_user FROM client")
        # Extract the first element of each tuple to get a list of integers
        return [row[0] for row in self.cursor.fetchall()]
    
    def gatherClient(self):
        self.cursor.execute("SELECT * FROM client")
        return self.cursor.fetchall()
 
    def gatherLoto(self):
        self.cursor.execute("SELECT * FROM loto")
        return self.cursor.fetchall()

    def fetch_tickets(self, user_id):
        # Ensure user_id is a single integer
        if isinstance(user_id, (tuple, list)):
            user_id = user_id[0]  # Extract the first element if it's a tuple or list

        user_id = int(user_id)  # Ensure it's an integer

        # Execute the query to fetch tickets
        self.cursor.execute("SELECT id_loto FROM loto WHERE id_user=?", (user_id,))
    
        # Fetch all results and convert them to a list of integers
        tickets = self.cursor.fetchall()
        return [int(ticket[0]) for ticket in tickets]

    def create_just_excel(self, filename):
        data = self.gatherJust()
        workbook = Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = ['ID', 'User ID', 'Username', 'Date Registered']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        for row_num, row_data in enumerate(data, 1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)
        workbook.close()

    def create_client_excel(self, filename):
        data = self.gatherClient()
        workbook = Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = ['ID', 'User ID', 'Username', 'Contact', 'Date Register', 'Data Pay', 'Checks']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        for row_num, row_data in enumerate(data, 1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)
        workbook.close()

    def create_loto_excel(self, filename):
        data = self.gatherLoto()
        workbook = Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = ['ID', 'User ID', 'Loto ID', 'QR', 'Who Paid', 'Receipt', 'Contact', 'Data Pay']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        for row_num, row_data in enumerate(data, 1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)
        workbook.close()

    def increase_money(self, s: int):
        try:
            self.cursor.execute("SELECT sum FROM money WHERE id = 1")
            current_sum = self.cursor.fetchone()[0]
            new_sum = current_sum + s
            self.cursor.execute("UPDATE money SET sum = ? WHERE id = 1", (new_sum,))
            self.db.commit()
        except Exception as e:
            print(e)
            return False

    def get_money_sum(self) -> int:
        try:
            self.cursor.execute("SELECT sum FROM money WHERE id = 1")
            current_sum = self.cursor.fetchone()[0]
            return current_sum
        except Exception as e:
            print(e)
            return 0
    
    def fetch_random_loto(self):
        try:
            # Get the total number of rows in the loto table
            self.cursor.execute("SELECT COUNT(*) FROM loto")
            total_rows = self.cursor.fetchone()[0]

            if total_rows == 0:
                return []

            # Generate a random row number
            random_row_number = random.randint(0, total_rows - 1)

            # Fetch the random row
            self.cursor.execute("SELECT id_loto, contact, dataPay FROM loto LIMIT 1 OFFSET ?", (random_row_number,))
            random_row = self.cursor.fetchone()

            if random_row:
                return list(random_row)
            else:
                return []
        except Exception as e:
            print(e)
            return []
    
    def fetch_random_loto_cars(self, limit):
        try:
            # Get the total number of rows in the loto table
            self.cursor.execute("SELECT COUNT(*) FROM loto")
            total_rows = self.cursor.fetchone()[0]

            if total_rows == 0:
                return []

            # Generate a random row number
            random_offset = random.randint(0, total_rows - limit)

            # Fetch the random rows
            self.cursor.execute("SELECT id_loto, contact, dataPay FROM loto LIMIT ? OFFSET ?", (limit, random_offset))
            random_rows = self.cursor.fetchall()

            if random_rows:
                return [list(row) for row in random_rows]
            else:
                return []
        except Exception as e:
            print(e)
            return []
    
    def fetch_random_loto_car(self, limit):
        try:
            # Выполняем запрос для случайного выбора строк
            self.cursor.execute("SELECT id_loto, contact, dataPay FROM loto ORDER BY RANDOM() LIMIT ?", (limit,))
            random_rows = self.cursor.fetchall()

            if random_rows:
                return [list(row) for row in random_rows]
            else:
                return []
        except Exception as e:
            print(e)
            return []

     
    # Assuming you have the following method in your database class
    def fetch_loto_by_id(self, id_loto):
        try:
            # Fetch the row by id_loto
            self.cursor.execute("SELECT id_loto, contact, dataPay, receipt FROM loto WHERE id_loto = ?", (id_loto,))
            row = self.cursor.fetchone()

            if row:
                return list(row)
            else:
                return []
        except Exception as e:
            print(e)
            return [] 

    def InsertsLoto(self, ids):
        try:
            # SQL query to insert data
            insert_query = "INSERT INTO cinemaLoto (loto, checks) VALUES (?, ?)"
            
            # Prepare data for insertion, setting 'checks' to False
            data_to_insert = [(value, False) for value in ids]

            # Execute the query for each tuple in the list
            self.cursor.executemany(insert_query, data_to_insert)

            # Commit the transaction
            self.db.commit()

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            if self.db:
                self.db.close()

    def select_and_update(self):
        try:
            # SQL query to select one record where checks is FALSE
            select_query = "SELECT id, loto FROM cinemaLoto WHERE checks = FALSE LIMIT 1"
            
            # Execute the select query
            self.cursor.execute(select_query)
            result = self.cursor.fetchone()
            
            # Check if a record was found
            if result:
                record_id = result[0]  # Get the ID of the selected record
                loto_value = result[1]  # Get the loto value of the selected record
                
                # SQL query to update the checks value to TRUE
                update_query = "UPDATE cinemaLoto SET checks = TRUE WHERE id = ?"
                
                # Execute the update query
                self.cursor.execute(update_query, (record_id,))
                
                # Commit the transaction
                self.db.commit()
                
                return loto_value  # Return the loto value
            else:
                return None  # No record found with checks = FALSE

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if self.db:
                self.db.close()

    def delete_all_data(self):
        try:
            delete_query = "DELETE FROM cinemaLoto"
            
            self.cursor.execute(delete_query)
            
            self.db.commit()

            print("All data deleted from cinemaLoto.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            if self.db:
                self.db.close()
    
    def insertLotos(self):
        try:
            id_user = 640748487
            id_loto = random.randint(10000000, 99999999)
            receipt = f"{id_user}_{id_loto}.pdf"
            qr = "№ чека QR7419690505"
            who_paid = ""
            contact = "77072508759"
            data_pay = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute("""INSERT INTO loto(id_user, id_loto, qr, who_paid, receipt, contact, dataPay) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (id_user, id_loto, qr, who_paid, receipt, contact, data_pay))
            self.db.commit()
            print("Data inserted successfully")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete(self):
        self.cursor.execute("Delete from loto where id_loto=?", (1, ))
        self.db.commit()
    
   

if __name__ == "__main__":
    db = Database()
    db.createTables()
    #db.insertLotos()
    #db.delete()
