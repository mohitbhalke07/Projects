from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import config
from datetime import datetime, timedelta
import MySQLdb.cursors
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Step 1: Configure MySQL
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

# Step 2: Initialize MySQL
mysql = MySQL(app)

# Custom Funtions
def get_user_by_credentials(username, password):
    try:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email=%s AND password=%s"
        cur.execute(query, (username, password))
        user = cur.fetchone()
        cur.close()
        return user
    except Exception as e:
        print(f"[ERROR] DB Exception: {e}")
        return None

@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return "✅ Database connection successful!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"


# Step 3: Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"[DEBUG] Attempting login with: {username}")

        user = get_user_by_credentials(username, password)
        print(f"[DEBUG] Fetched user: {user}")

        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/')

    # today = datetime.today().date()
    # default_start = today - timedelta(days=30)
    # default_end = today

    # start_date = request.form.get('start_date') or default_start.strftime('%Y-%m-%d')
    # end_date = request.form.get('end_date') or default_end.strftime('%Y-%m-%d')

    # Set default dates to fixed values
    default_start = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
    default_end = datetime.strptime('2024-02-01', '%Y-%m-%d').date()

    # Use form input if provided, otherwise fall back to defaults
    start_date = request.form.get('start_date') or default_start.strftime('%Y-%m-%d')
    end_date = request.form.get('end_date') or default_end.strftime('%Y-%m-%d')


    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch full table data for table display
        cur.execute("SELECT * FROM predicted_data WHERE Transaction_Date BETWEEN %s AND %s", (start_date, end_date))
        data = cur.fetchall()

        # Bar Chart: Fraudulent vs Non-Fraudulent by Payment Method
        cur.execute("""
            SELECT payment_method, 
                   SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent_count,
                   SUM(CASE WHEN is_fraudulent = 0 THEN 1 ELSE 0 END) AS non_fraudulent_count
            FROM predicted_data
            WHERE Transaction_Date BETWEEN %s AND %s
            GROUP BY payment_method
        """, (start_date, end_date))
        payment_data = cur.fetchall()
        payment_method_labels = [item['payment_method'] for item in payment_data]
        fraudulent_counts = [item['fraudulent_count'] for item in payment_data]
        non_fraudulent_counts = [item['non_fraudulent_count'] for item in payment_data]

        # Pie Chart: Devices Used with Fraudulent vs Non-Fraudulent
        cur.execute("""
            SELECT device_used, 
                SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent_count,
                SUM(CASE WHEN is_fraudulent = 0 THEN 1 ELSE 0 END) AS non_fraudulent_count
            FROM predicted_data
            WHERE Transaction_Date BETWEEN %s AND %s
            GROUP BY device_used
        """, (start_date, end_date))
        devices_data = cur.fetchall()
        devices_labels = [item['device_used'] for item in devices_data]
        fraudulent_device_counts = [item['fraudulent_count'] for item in devices_data]
        non_fraudulent_device_counts = [item['non_fraudulent_count'] for item in devices_data]

        # Line Chart: Fraudulent Transactions Over Time
        cur.execute("""
            SELECT transaction_date, COUNT(*) AS fraudulent_count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY transaction_date
            ORDER BY transaction_date
        """, (start_date, end_date))
        fraud_time_data = cur.fetchall()
        date_labels = [item['transaction_date'].strftime('%Y-%m-%d') for item in fraud_time_data]
        fraudulent_transactions = [item['fraudulent_count'] for item in fraud_time_data]

        # 1. Product Category vs Fraudulent Transactions
        cur.execute("""
            SELECT product_category, COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY product_category
        """, (start_date, end_date))
        fraud_by_category = cur.fetchall()

        # 2. Age Group vs Fraudulent Transactions
        cur.execute("""
            SELECT 
                CASE 
                    WHEN customer_age BETWEEN 18 AND 25 THEN '18-25'
                    WHEN customer_age BETWEEN 26 AND 35 THEN '26-35'
                    WHEN customer_age BETWEEN 36 AND 45 THEN '36-45'
                    WHEN customer_age BETWEEN 46 AND 60 THEN '46-60'
                    ELSE '60+' 
                END AS age_group,
                COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY age_group
        """, (start_date, end_date))
        fraud_by_age_group = cur.fetchall()

        # 3. Location vs Fraudulent Transactions
        cur.execute("""
            SELECT customer_location, COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY customer_location
        """, (start_date, end_date))
        fraud_by_location = cur.fetchall()

        # 4. Transaction Amount Range vs Fraudulent Transactions
        cur.execute("""
            SELECT 
                CASE 
                    WHEN transaction_amount < 100 THEN '<100'
                    WHEN transaction_amount BETWEEN 100 AND 499 THEN '100-499'
                    WHEN transaction_amount BETWEEN 500 AND 999 THEN '500-999'
                    ELSE '1000+' 
                END AS amount_range,
                COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY amount_range
        """, (start_date, end_date))
        fraud_by_amount_range = cur.fetchall()

        # 5. Account Age Days vs Fraudulent Transactions
        cur.execute("""
            SELECT 
                CASE 
                    WHEN account_age_days < 30 THEN '<30 days'
                    WHEN account_age_days BETWEEN 30 AND 180 THEN '30-180 days'
                    ELSE '180+ days' 
                END AS age_range,
                COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY age_range
        """, (start_date, end_date))
        fraud_by_account_age = cur.fetchall()

        # 6. Transaction Hour vs Fraudulent Transactions
        cur.execute("""
            SELECT transaction_hour, COUNT(*) AS count
            FROM predicted_data
            WHERE is_fraudulent = 1 AND Transaction_Date BETWEEN %s AND %s
            GROUP BY transaction_hour
            ORDER BY transaction_hour
        """, (start_date, end_date))
        fraud_by_hour = cur.fetchall()

        # 7. Payment Method vs Fraud Rate
        cur.execute("""
            SELECT 
                payment_method,
                ROUND(100 * SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate
            FROM predicted_data
            WHERE Transaction_Date BETWEEN %s AND %s
            GROUP BY payment_method
        """, (start_date, end_date))
        fraud_rate_by_payment_method = cur.fetchall()

        # Extract data for charts
        category_labels = [row['product_category'] for row in fraud_by_category]
        category_fraud_counts = [row['count'] for row in fraud_by_category]

        age_group_labels = [row['age_group'] for row in fraud_by_age_group]
        age_group_fraud_counts = [row['count'] for row in fraud_by_age_group]

        hour_labels = [row['transaction_hour'] for row in fraud_by_hour]
        hour_fraud_counts = [row['count'] for row in fraud_by_hour]

        sorted_locations = sorted(fraud_by_location, key=lambda x: x['count'], reverse=True)[:10]
        top_locations = [row['customer_location'] for row in sorted_locations]
        top_location_fraud_counts = [row['count'] for row in sorted_locations]

        account_age_bins = [row['age_range'] for row in fraud_by_account_age]
        account_age_fraud_counts = [row['count'] for row in fraud_by_account_age]

        quantity_labels = []  # Add logic for quantity chart if needed
        quantity_fraud_counts = []

        payment_method_labels_rate = [row['payment_method'] for row in fraud_rate_by_payment_method]
        fraud_percentages = [row['fraud_rate'] for row in fraud_rate_by_payment_method]

        cur.close()

        return render_template('dashboard.html',
                               data=data,
                               start_date=start_date,
                               end_date=end_date,
                               payment_method_labels=payment_method_labels,
                               fraudulent_counts=fraudulent_counts,
                               non_fraudulent_counts=non_fraudulent_counts,
                               devices_labels=devices_labels,
                               fraudulent_device_counts=fraudulent_device_counts,
                               non_fraudulent_device_counts=non_fraudulent_device_counts,
                               date_labels=date_labels,
                               fraudulent_transactions=fraudulent_transactions,
                               # New insights
                               category_labels=category_labels,
                               category_fraud_counts=category_fraud_counts,
                               age_group_labels=age_group_labels,
                               age_group_fraud_counts=age_group_fraud_counts,
                               hour_labels=hour_labels,
                               hour_fraud_counts=hour_fraud_counts,
                               top_locations=top_locations,
                               top_location_fraud_counts=top_location_fraud_counts,
                               account_age_bins=account_age_bins,
                               account_age_fraud_counts=account_age_fraud_counts,
                               fraud_percentages=fraud_percentages,
                               payment_method_labels_rate=payment_method_labels_rate,
                               quantity_labels=quantity_labels,
                               quantity_fraud_counts=quantity_fraud_counts)

    except Exception as e:
        print(f"[ERROR] Dashboard DB fetch: {e}")
        return render_template('dashboard.html',
                               data=[],
                               start_date=start_date,
                               end_date=end_date,
                               payment_method_labels=[],
                               fraudulent_counts=[],
                               non_fraudulent_counts=[],
                               devices_labels=[],
                               fraudulent_device_counts=[],
                               non_fraudulent_device_counts=[],
                               date_labels=[],
                               fraudulent_transactions=[],
                               fraud_by_category=[],
                               fraud_by_age_group=[],
                               fraud_by_location=[],
                               fraud_by_amount_range=[],
                               fraud_by_account_age=[],
                               fraud_by_hour=[],
                               fraud_rate_by_payment_method=[])





@app.route('/sync', methods=['POST'])
def sync():
    print("SYNC BUTTON CLICKED")
    try:
        print("Loading test CSV file...")
        file_path = 'Fraudulent_E-Commerce_Transaction_Data_Test.csv'
        test_data = pd.read_csv(file_path)
        print(f"Loaded {len(test_data)} total records.")

        # If `is_processed` column doesn't exist, add it
        if 'is_processed' not in test_data.columns:
            print("Adding 'is_processed' column...")
            test_data['is_processed'] = 0
            test_data.to_csv(file_path, index=False)

        # Check for records that are not processed
        unprocessed_data = test_data[test_data['is_processed'] == 0]
        print(f"Found {len(unprocessed_data)} unprocessed records.")

        if len(unprocessed_data) == 0:
            print("No unprocessed records left.")
            return redirect('/dashboard')

        # Take only 20 records for prediction
        # records_to_process = unprocessed_data.head(20)
        records_to_process = unprocessed_data.sample(n=20, random_state=42)  # random_state for reproducibility
        original_indices = records_to_process.index.tolist()
        print("Processing 20 records...")
        records_to_process = records_to_process.reset_index(drop=True)

        # Load trained model and preprocessors
        print("Loading model and encoders...")
        model = joblib.load('model/xgb_fraud_model.pkl')
        encoder = joblib.load('model/target_encoder.pkl')
        preprocessor = joblib.load('model/columntransformer_preprocessor.pkl')

        # Drop unnecessary columns
        columns_to_keep = [
            'Transaction Amount', 'Transaction Date', 'Payment Method', 'Product Category',
            'Quantity', 'Customer Age', 'Customer Location', 'Device Used',
            'Account Age Days', 'Transaction Hour'
        ]
        columns_to_keep_output = [
            'Transaction Amount', 'Transaction Date', 'Payment Method', 'Product Category',
            'Quantity', 'Customer Age', 'Customer Location', 'Device Used',
            'Account Age Days', 'Transaction Hour', 'Is Fraudulent'
        ]
        records_to_process_actual = records_to_process[columns_to_keep_output]
        records_to_process = records_to_process[columns_to_keep]
        # print("Columns in records_to_process:", records_to_process_actual.columns.tolist())
        print("Columns selected.")

        # Convert 'Transaction Date' to datetime
        records_to_process['Transaction Date'] = pd.to_datetime(records_to_process['Transaction Date'])
        print("Converted 'Transaction Date' to datetime.")

        # Encode 'Customer Location'
        print("Encoding 'Customer Location'...")
        records_to_process = encoder.transform(records_to_process)
        print("Encoding complete.")

        # Preprocess features
        print("Preprocessing features...")
        X_processed = preprocessor.transform(records_to_process)
        print("Preprocessing complete.")

        # Predict
        print("Making predictions...")
        predictions = model.predict(X_processed)
        print("Predictions done.")

        # Insert predictions into the database
        print("Inserting predictions into the database...")
        cur = mysql.connection.cursor()
        for idx, row in records_to_process_actual.iterrows():
            cur.execute("""
                INSERT INTO predicted_data (
                    transaction_amount, transaction_date, payment_method, product_category,
                    quantity, customer_age, customer_location, device_used, is_fraudulent,is_fraudulent_actual,
                    account_age_days, transaction_hour
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['Transaction Amount'],
                row['Transaction Date'],
                row['Payment Method'],
                row['Product Category'],
                row['Quantity'],
                row['Customer Age'],
                row['Customer Location'],
                row['Device Used'],
                int(predictions[idx]),
                row['Is Fraudulent'],
                row['Account Age Days'],
                row['Transaction Hour']
            ))

            # Mark the record as processed
            test_data.at[original_indices[idx], 'is_processed'] = 1

        test_data.to_csv(file_path, index=False)
        mysql.connection.commit()
        cur.close()
        print("Records successfully saved and marked as processed.")

    except Exception as e:
        print("An error occurred during sync:", str(e))

    return redirect('/dashboard')




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    print("✅ Flask app starting...")
    app.run(debug=True)
