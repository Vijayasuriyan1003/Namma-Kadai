from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myshop'

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')
@app.route('/regester', methods=['GET','POST'])
def regester():
    return render_template('registration.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    username = request.form['username']
    password = request.form['password']
    bal = int(request.form['balance'])
    statement = "Registration Successful"

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute('INSERT INTO company (companyname, balance, c_password) VALUES (%s, %s, %s);',
                   (username, bal, password))

    conn.commit()
    cursor.close()

    return render_template('login.html', statement=statement)


@app.route('/home', methods=['POST'])
def home():
    c_name = request.form['uname']
    passw = request.form['password']

    conn = mysql.connection.cursor()
    conn.execute('SELECT companyname, c_password, balance FROM company WHERE companyname = %s', (c_name,))
    user_data = conn.fetchone()
    conn.close()

    if user_data:
        username, password, balance = user_data
        if passw == password:
            return render_template('index.html', balance=balance)
        else:
            statement = "Enter correct password"
            return render_template('login.html', statement=statement)
    else:
        statement = "User not found"
        return render_template('login.html', statement=statement)

@app.route('/add_item', methods=['POST'])
def add_item():
        item_name = request.form.get('item_name')
        item_quantity = int(request.form.get('purchaseQuantity'))
        price_value = int(request.form.get('sellPrice'))

        statement=""

        conn = mysql.connection.cursor()
        conn.execute('SELECT balance FROM company')
        prebalance = conn.fetchone()[0]


        conn.execute('INSERT INTO item(itemname, itemquantity) VALUES (%s, %s)', (item_name, item_quantity))
        item_id = conn.lastrowid

        total_purchase_amount = item_quantity * price_value
        price_per_item = price_value

        if total_purchase_amount>prebalance:
            statement="your balance is low!!!!"
            return render_template('index.html', statement1=statement, balance=prebalance)
        else:
            conn.execute('SELECT itemname FROM item')
            iname=conn.fetchone()

            statement = "Item added successfully!"
            balance=prebalance-total_purchase_amount
            if item_name in iname:
                conn.execute('SELECT itemquantity FROM item where itemname =%s',(item_name,))
                prequant=conn.fetchone()[0]
                conn.execute('UPDATE item SET itemquantity=%s WHERE itemname =%s;', (prequant+item_quantity,item_name))
            conn.execute('INSERT INTO purchase (itemid, priceperitem, totalprice, prebalance, balance) VALUES (%s, %s, %s, %s, %s)', (item_id, price_per_item, total_purchase_amount, prebalance, balance))
            conn.execute('UPDATE company SET balance=%s WHERE companyid = 1;', (balance,))
            conn.connection.commit()
            conn.close()
            return  render_template('index.html', statement1=statement, balance=balance)

@app.route('/sell_item', methods=['POST'])
def sell_item():
    if request.method == "POST":
        item_name = request.form.get('sellItem')
        item_quantity = int(request.form.get('sellQuantity'))
        price_value = int(request.form.get('sellPrice'))

        statement = ""

        conn = mysql.connection.cursor()
        conn.execute('SELECT itemid, itemquantity FROM item WHERE itemname = %s', (item_name,))
        item_data = conn.fetchone()
        conn.execute('SELECT balance FROM company')
        prebalance = conn.fetchone()[0]

        if item_data:
            item_id, available_quantity = item_data

            if item_quantity > available_quantity:
                statement = "Insufficient quantity available for sale"
                return render_template('index.html', statement2=statement, balance=prebalance)
            else:
                total_sale_amount = item_quantity * price_value
                new_quantity = available_quantity - item_quantity
                balance = prebalance + total_sale_amount

                conn.execute('UPDATE item SET itemquantity = %s WHERE itemid = %s', (new_quantity, item_id))
                conn.execute('INSERT INTO sales (itemid, soldpriceperitem, totalsoldprice, pretotals, balances) VALUES (%s, %s, %s, %s, %s)',
                             (item_id, price_value, total_sale_amount, prebalance, balance))
                conn.execute('UPDATE company SET balance = %s WHERE companyid = 1', (balance,))
                conn.connection.commit()
                statement = "Item sold successfully!"
                return render_template('index.html', statement2=statement, balance=balance)
        else:
            statement = "Item not found"
            return render_template('index.html', statement2=statement, balance=prebalance)

        conn.close()

@app.route('/purchase_report')
def purchase_report():
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM purchase')
    purchases = conn.fetchall()
    conn.execute('SELECT * FROM item')
    item = conn.fetchall()
    conn.close()

    return render_template('purchasereport.html', purchases=purchases, item=item)


@app.route('/sales_report')
def sales_report():
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM sales')
    sales = conn.fetchall()
    conn.close()

    return render_template('salesreport.html', sales=sales)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
