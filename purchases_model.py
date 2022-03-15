class PurchaseModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS purchases 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             tovar VARCHAR(99),  
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER,
                             phone VARCHAR (20),
                             count_ INTEGER 
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, tovar, title, content, user_id,count,phone):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO purchases 
                          (tovar, title, content, user_id,count_,phone) 
                          VALUES (?,?,?,?,?,?)''', (tovar, title, content, str(user_id),str(count),phone))
        cursor.close()
        self.connection.commit()

    def get(self, purchases_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM purchases WHERE id = ?", (str(purchases_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM purchases WHERE user_id = ?",
                           (str(user_id),))
        else:
            cursor.execute("SELECT * FROM purchases")
        rows = cursor.fetchall()
        return rows

    def delete(self, purchases_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM purchases WHERE id = ?''', (str(purchases_id),))
        cursor.close()
        self.connection.commit()

    def get_user_id(self, purchases_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT user_id FROM purchases WHERE id = ?", (str(purchases_id),))
        row = cursor.fetchone()
        return row

