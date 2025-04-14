from flask import Flask, jsonify, request, render_template, redirect, url_for, redirect, session, flash
import requests
import pymysql
import mysql.connector
from flask_cors import CORS
import os
import base64
import bcrypt
import uuid
import datetime
import secrets
from functools import wraps
from db import get_db_connection
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
# Get the secret key from environment variables with no fallback to ensure it's set
app.secret_key = os.environ["SECRET_KEY"]

# Configure session
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours (in seconds)

CORS(app)

# User authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


# API keys (check if they are loaded correctly)
GEO_API_KEY = os.getenv("GEO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "chemphymath2002@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "Tarak@2002")
EMAIL_FROM = os.getenv("EMAIL_FROM", "chemphymath2002@gmail.com")

# Check if any API keys are missing
if not GEO_API_KEY or not GEMINI_API_KEY or not GEMINI_MODEL_NAME:
    print("Error: Missing one or more API keys.")
    exit(1)

# Function to send emails
def send_email(to_email, subject, html_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()  # Identify ourselves to the server
        server.starttls()  # Secure the connection
        server.ehlo()  # Re-identify ourselves over TLS connection
        
        # Login with the provided credentials
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send the email
        server.send_message(msg)
        server.quit()
        
        print(f"Password reset email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Failed to authenticate with Gmail. Please check your email credentials.")
        print("Note: For Gmail, you may need to:")
        print("1. Enable 'Less secure app access' in your Google account settings, or")
        print("2. Use an App Password if you have 2-factor authentication enabled")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Generate a random 6-digit OTP
def generate_otp():
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

# Send OTP via email
def send_otp_email(email, otp, purpose="verification"):
    user_name = email.split('@')[0]  # Simple fallback name
    
    # Get user's name if available
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                user_name = user['name']
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Error fetching user name: {str(e)}")
    
    # Prepare email content
    if purpose == "password_reset":
        subject = "Password Reset OTP - Restaurant Finder"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #e7460b; margin-bottom: 5px;">Password Reset Request</h2>
                    <div style="height: 3px; background-color: #e7460b; width: 100px; margin: 0 auto;"></div>
                </div>
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password for your Restaurant Finder account.</p>
                <div style="background-color: #fff; padding: 15px; border-radius: 5px; border: 1px solid #eee; margin: 20px 0; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Your password reset OTP is:</p>
                    <h2 style="font-size: 28px; letter-spacing: 5px; margin: 10px 0; color: #e7460b; font-weight: bold;">{otp}</h2>
                    <p style="margin: 0; font-size: 12px; color: #999;">This code will expire in 15 minutes</p>
                </div>
                <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
                <p>Best regards,<br>The Restaurant Finder Team</p>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; text-align: center;">
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        subject = "Verification OTP - Restaurant Finder"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #e7460b;">Email Verification</h2>
                <p>Hello {user_name},</p>
                <p>Thank you for using Restaurant Finder. Please use the following OTP to verify your email address:</p>
                <p><strong style="font-size: 18px; letter-spacing: 2px;">{otp}</strong></p>
                <p>This OTP will expire in 15 minutes.</p>
                <p>If you did not request this verification, please ignore this email.</p>
                <p>Best regards,<br>The Restaurant Finder Team</p>
            </div>
        </body>
        </html>
        """
    
    # Send the email
    return send_email(email, subject, body)



@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login_page'))

@app.route("/home")
@login_required
def home():
    return render_template('first_page.html')

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    login_error = None
    register_error = None
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            login_error = "Email and password are required"
            return render_template('login.html', login_error=login_error)
        
        connection = get_db_connection()
        if not connection:
            login_error = "Database connection failed"
            return render_template('login.html', login_error=login_error)
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                return redirect(url_for('home'))
            else:
                login_error = "Invalid email or password"
        except Exception as e:
            login_error = f"An error occurred: {str(e)}"
    
    return render_template('login.html', login_error=login_error, register_error=register_error)

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate form data
    if not name or not email or not password or not confirm_password:
        return render_template('login.html', register_error="All fields are required", form="register")
    
    if password != confirm_password:
        return render_template('login.html', register_error="Passwords do not match", form="register")
    
    # Check if email already exists
    connection = get_db_connection()
    if not connection:
        return render_template('login.html', register_error="Database connection failed", form="register")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            connection.close()
            return render_template('login.html', register_error="Email already registered", form="register")
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, hashed_password.decode('utf-8'))
        )
        connection.commit()
        
        # Get the new user's ID
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        new_user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Log the user in
        session['user_id'] = new_user['id']
        session['user_name'] = name
        session['user_email'] = email
        
        return redirect(url_for('home'))
    
    except Exception as e:
        return render_template('login.html', register_error=f"Registration failed: {str(e)}", form="register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route("/forgot-password-test")
def forgot_password_test():
    return render_template('forgot_password_test.html')

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')
        
        if not email:
            return render_template('basic_reset.html', error="Email is required")
        
        connection = get_db_connection()
        if not connection:
            return render_template('basic_reset.html', error="Database connection failed")
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                # Don't reveal if email exists or not for security
                # We'll return a success message even if the email doesn't exist
                # This prevents user enumeration attacks
                return render_template('basic_reset.html', 
                                      message="A password reset OTP has been sent to your email address. Please check your inbox and spam folder.", 
                                      success=True)
            
            # Generate a 6-digit OTP
            otp = generate_otp()
            # OTP expires in 15 minutes
            expiry = datetime.datetime.now() + datetime.timedelta(minutes=15)
            
            # Store the OTP in the database
            cursor.execute(
                "INSERT INTO password_reset_tokens (user_id, token, expiry) VALUES (%s, %s, %s)",
                (user['id'], otp, expiry)
            )
            connection.commit()
            
            # Send the OTP via email
            email_sent = send_otp_email(email, otp, purpose="password_reset")
            
            cursor.close()
            connection.close()
            
            # Always hide the OTP in the response for security
            if email_sent:
                return render_template('basic_reset.html', 
                                      message="A password reset OTP has been sent to your email address. Please check your inbox and spam folder.", 
                                      success=True)
            else:
                return render_template('basic_reset.html', 
                                      error="There was a problem sending the email. Please try again later or contact support.", 
                                      success=False)
            
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            return render_template('basic_reset.html', error=f"An error occurred: {str(e)}")
    
    # For GET requests, show the form
    return render_template('basic_reset.html')

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        otp = request.form.get('token')  # Using 'token' field for OTP for backward compatibility
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not email or not otp or not password or not confirm_password:
            return render_template('basic_reset.html', 
                                  error="All fields are required", 
                                  verify=True)
        
        if password != confirm_password:
            return render_template('basic_reset.html', 
                                  error="Passwords do not match", 
                                  verify=True,
                                  email=email,
                                  token=otp)
        
        connection = get_db_connection()
        if not connection:
            return render_template('basic_reset.html', 
                                  error="Database connection failed", 
                                  verify=True)
        
        try:
            cursor = connection.cursor()
            
            # Get user ID from email
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                connection.close()
                return render_template('basic_reset.html', 
                                      error="Invalid email or OTP", 
                                      verify=True)
            
            # Check if OTP is valid
            cursor.execute(
                """
                SELECT id FROM password_reset_tokens 
                WHERE user_id = %s AND token = %s AND expiry > %s AND used = 0
                ORDER BY created_at DESC LIMIT 1
                """, 
                (user['id'], otp, datetime.datetime.now())
            )
            otp_record = cursor.fetchone()
            
            if not otp_record:
                cursor.close()
                connection.close()
                return render_template('basic_reset.html', 
                                      error="Invalid or expired OTP", 
                                      verify=True)
            
            # Hash the new password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Update the user's password
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (hashed_password.decode('utf-8'), user['id'])
            )
            
            # Mark the OTP as used
            cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = %s", (otp_record['id'],))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            # Store success message in session
            session['flash_message'] = "Your password has been reset successfully. Please log in with your new password."
            return redirect(url_for('login_page', reset_success=True))
            
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            return render_template('basic_reset.html', 
                                  error=f"An error occurred: {str(e)}", 
                                  verify=True)
    
    # For GET requests, show the verification form
    return render_template('basic_reset.html', verify=True)

@app.route('/restaurants', methods=['GET'])
@login_required
def get_restaurants():
    try:
        search_term = request.args.get('search', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 9, type=int)
        offset = (page - 1) * per_page

        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()

        cursor.execute("""
            SELECT Restaurant_ID, Restaurant_Name, Country_Code, City, Address, Locality, Longitude, Latitude, Cuisine, 
                Avg_Cost_for_Two, Currency, Has_Table_booking, Has_Online_delivery, Is_delivering_now, Switch_to_order_menu, Price_Range, 
                Rating, Rating_Color, Rating_Text, Total_Votes, City_ID, featured_image, photos_url, menu_url, events_url, 
                Restaurant_URL, Location_Zipcode, Country 
            FROM zomato_new
            WHERE Restaurant_Name LIKE %s
            LIMIT %s OFFSET %s
        """, ('%' + search_term + '%', per_page, offset))

        restaurants = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM zomato_new WHERE Restaurant_Name LIKE %s", ('%' + search_term + '%',))
        total_records = cursor.fetchone()['total']

        cursor.close()
        connection.close()

        # For API requests, return JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'restaurants': restaurants,
                'total': total_records,
                'pages': (total_records // per_page) + (1 if total_records % per_page > 0 else 0),
                'current_page': page
            }), 200
        
        # For browser requests, render the template
        return render_template('search_results.html', 
                              restaurants=restaurants,
                              total=total_records,
                              pages=(total_records // per_page) + (1 if total_records % per_page > 0 else 0),
                              current_page=page,
                              per_page=per_page,
                              search_term=search_term)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/restaurant', methods=['GET'])
@login_required
def get_restaurant_details():
    try:
        restaurant_name = request.args.get('name', '', type=str)

        if not restaurant_name:
            return jsonify({"error": "Restaurant name is required"}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()

        cursor.execute("""
            SELECT Restaurant_ID, Restaurant_Name, Country_Code, City, Address, Locality, Longitude, Latitude, Cuisine, 
                Avg_Cost_for_Two, Currency, Has_Table_booking, Has_Online_delivery, Is_delivering_now, Switch_to_order_menu, Price_Range, 
                Rating, Rating_Color, Rating_Text, Total_Votes, City_ID, featured_image, photos_url, menu_url, events_url, 
                Restaurant_URL, Location_Zipcode, Country 
            FROM zomato_new
            WHERE Restaurant_Name = %s
        """, (restaurant_name,))

        restaurant = cursor.fetchone()

        cursor.close()
        connection.close()

        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        # For API requests, return JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify(restaurant), 200
        
        # For browser requests, render the template
        return render_template('restaurant_details.html', restaurant=restaurant)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/restaurants/names', methods=['GET'])
@login_required
def get_restaurant_names():
    try:
        search_term = request.args.get('search', '', type=str)
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)

        if latitude is not None and longitude is not None:
            global temporary_restaurant_db
            filtered_restaurants = [
                restaurant for restaurant in temporary_restaurant_db
                if search_term.lower() in restaurant['Restaurant_Name'].lower()
            ]
            # Get unique restaurant names
            restaurant_names = list(set([restaurant['Restaurant_Name'] for restaurant in filtered_restaurants]))
            # Sort alphabetically for better user experience
            restaurant_names.sort()
            return jsonify({'restaurants': restaurant_names}), 200

        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        # Use DISTINCT to get only unique restaurant names
        cursor.execute("SELECT DISTINCT Restaurant_Name FROM zomato_new WHERE Restaurant_Name LIKE %s ORDER BY Restaurant_Name LIMIT 30", ('%' + search_term + '%',))
        restaurant_names = [row['Restaurant_Name'] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        return jsonify({'restaurants': restaurant_names}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/location', methods=['GET'])
@login_required
def location_page():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return redirect(url_for('home'))
        
    return render_template('location.html')

from flask import Flask, request, jsonify, abort
from functools import wraps
import mysql.connector
import math

@app.route('/fetch_nearby_restaurants', methods=['GET'])
@login_required
def fetch_nearby_restaurants():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required!"}), 400

    radius_km = 3  # 3 km

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed!"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                Restaurant_ID, Restaurant_Name, Country_Code, City, Address, Locality,
                Longitude, Latitude, Cuisine, Avg_Cost_for_Two, Currency, Has_Table_booking,
                Has_Online_delivery, Is_delivering_now, Switch_to_order_menu, Price_Range,
                Rating, Rating_Color, Rating_Text, Total_Votes, City_ID, featured_image,
                photos_url, menu_url, events_url, Restaurant_URL, Location_Zipcode, Country,
                (
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(Latitude)) *
                        cos(radians(Longitude) - radians(%s)) +
                        sin(radians(%s)) * sin(radians(Latitude))
                    )
                ) AS distance
            FROM restaurants
            HAVING distance <= %s
            ORDER BY distance ASC
            LIMIT 10;
        """

        cursor.execute(query, (lat, lon, lat, radius_km))
        results = cursor.fetchall()
        conn.close()

        if results:
            return jsonify(results), 200
        else:
            return jsonify({"message": "No nearby restaurants found in database."}), 404

    except Exception as e:
        return jsonify({"error": "Query failed", "details": str(e)}), 500

@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM restaurants WHERE Restaurant_ID = %s"
            cursor.execute(query, (restaurant_id,))
            restaurant = cursor.fetchone()

        if restaurant:
            restaurant.pop("id", None)
            return jsonify({"status": "success", "restaurant": restaurant}), 200
        else:
            return jsonify({"status": "error", "message": "Restaurant not found"}), 404

    except pymysql.MySQLError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        conn.close()

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        image = request.files['image']
        
        # Check if we're using mock API keys (for testing/development)
        if GEMINI_API_KEY == "mock_gemini_api_key" or GEMINI_MODEL_NAME == "gemini-pro-vision":
            print("Using mock response for image analysis (API keys not properly configured)")
            # Return a mock response for testing purposes
            # This will randomly select one of these cuisines
            import random
            mock_cuisines = ["pizza", "burger", "pasta", "sushi", "indian", "mexican", "chinese", "thai"]
            detected_cuisine = random.choice(mock_cuisines)
            return jsonify({"cuisine": detected_cuisine, "note": "This is a mock response for testing"})
        
        # If we have proper API keys, proceed with the actual API call
        base64_image = base64.b64encode(image.read()).decode('utf-8')

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Identify the cuisine type shown in the image. Only return the name of the cuisine like Pizza,Burger,Rice Bowl,Fish,Noodles nothing else."},
                        {"inlineData": {"mimeType": "image/jpeg", "data": base64_image}}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code}, Response: {response.text}")
            return jsonify({"error": f"API Error: {response.status_code}"}), 500
            
        result = response.json()

        if result.get("candidates"):
            detected_cuisine = result["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
            return jsonify({"cuisine": detected_cuisine})
        else:
            print(f"Unexpected API response: {result}")
            return jsonify({"error": "Could not recognize the image"}), 400

    except Exception as e:
        import traceback
        print(f"Error in analyze_image: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        
        connection = get_db_connection()
        if not connection:
            abort(500)
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not user or not user['is_admin']:
                abort(403)  # Forbidden
                
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Admin check error: {str(e)}")
            abort(500)
            
    return decorated_function

# Admin dashboard route
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Admin theme settings route
@app.route("/admin/theme")
@admin_required
def admin_theme():
    connection = get_db_connection()
    if not connection:
        abort(500)
    
    try:
        cursor = connection.cursor()
        
        # First check if the site_settings table exists
        try:
            cursor.execute("SELECT setting_value FROM site_settings WHERE setting_key = 'color_theme'")
            theme_setting = cursor.fetchone()
            current_theme = theme_setting['setting_value'] if theme_setting else 'orange'
        except mysql.connector.Error as err:
            # If table doesn't exist, create it
            if err.errno == 1146:  # "Table doesn't exist" error
                try:
                    # Create the site_settings table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_settings` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `setting_key` varchar(255) NOT NULL UNIQUE,
                      `setting_value` text NOT NULL,
                      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    
                    # Insert default color theme
                    cursor.execute("""
                    INSERT INTO site_settings (setting_key, setting_value) 
                    VALUES ('color_theme', 'orange')
                    """)
                    connection.commit()
                    current_theme = 'orange'
                except Exception as create_err:
                    print(f"Error creating site_settings table: {create_err}")
                    current_theme = 'orange'
            else:
                print(f"Database error: {err}")
                current_theme = 'orange'
        
        cursor.close()
        connection.close()
        
        return render_template('admin_theme.html', current_theme=current_theme)
    except Exception as e:
        print(f"Admin theme error: {str(e)}")
        abort(500)

# Save theme preference
@app.route("/admin/save_theme", methods=['POST'])
@admin_required
def save_theme():
    try:
        data = request.get_json()
        theme = data.get('theme')
        
        if not theme:
            return jsonify({"success": False, "error": "Theme is required"}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        # First check if the site_settings table exists
        try:
            cursor.execute(
                "INSERT INTO site_settings (setting_key, setting_value) VALUES ('color_theme', %s) "
                "ON DUPLICATE KEY UPDATE setting_value = %s",
                (theme, theme)
            )
            connection.commit()
        except mysql.connector.Error as err:
            # If table doesn't exist, create it
            if err.errno == 1146:  # "Table doesn't exist" error
                try:
                    # Create the site_settings table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_settings` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `setting_key` varchar(255) NOT NULL UNIQUE,
                      `setting_value` text NOT NULL,
                      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    
                    # Insert the theme
                    cursor.execute(
                        "INSERT INTO site_settings (setting_key, setting_value) VALUES ('color_theme', %s)",
                        (theme,)
                    )
                    connection.commit()
                except Exception as create_err:
                    print(f"Error creating site_settings table: {create_err}")
                    return jsonify({"success": False, "error": str(create_err)}), 500
            else:
                print(f"Database error: {err}")
                return jsonify({"success": False, "error": str(err)}), 500
        
        cursor.close()
        connection.close()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Save theme error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Get current theme (for all pages)
@app.route("/api/current_theme", methods=['GET'])
def get_current_theme():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"theme": "orange"}), 200  # Default if DB connection fails
        
        cursor = connection.cursor()
        
        # First check if the site_settings table exists
        try:
            cursor.execute("SELECT setting_value FROM site_settings WHERE setting_key = 'color_theme'")
            theme_setting = cursor.fetchone()
            current_theme = theme_setting['setting_value'] if theme_setting else 'orange'
        except mysql.connector.Error as err:
            # If table doesn't exist, create it
            if err.errno == 1146:  # "Table doesn't exist" error
                try:
                    # Create the site_settings table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_settings` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `setting_key` varchar(255) NOT NULL UNIQUE,
                      `setting_value` text NOT NULL,
                      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    
                    # Insert default color theme
                    cursor.execute("""
                    INSERT INTO site_settings (setting_key, setting_value) 
                    VALUES ('color_theme', 'orange')
                    """)
                    connection.commit()
                    current_theme = 'orange'
                    
                    # Also check if users table has is_admin column
                    try:
                        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin'")
                        if not cursor.fetchone():
                            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE")
                            cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = 'admin@example.com'")
                            connection.commit()
                    except Exception as e:
                        print(f"Error checking/adding is_admin column: {e}")
                        
                except Exception as create_err:
                    print(f"Error creating site_settings table: {create_err}")
                    current_theme = 'orange'
            else:
                print(f"Database error: {err}")
                current_theme = 'orange'
        
        cursor.close()
        connection.close()
        
        return jsonify({"theme": current_theme}), 200
    except Exception as e:
        print(f"Get theme error: {str(e)}")
        return jsonify({"theme": "orange"}), 200  # Default if error

# Hidden developer route for theme management
@app.route("/dev/z9x8y7w6v5u4")
def dev_theme():
    return render_template('dev_theme.html')

# Save theme preference (developer route)
@app.route("/dev/save_theme", methods=['POST'])
def dev_save_theme():
    try:
        data = request.get_json()
        theme = data.get('theme')
        
        if not theme:
            return jsonify({"success": False, "error": "Theme is required"}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        # First check if the site_settings table exists
        try:
            cursor.execute(
                "INSERT INTO site_settings (setting_key, setting_value) VALUES ('color_theme', %s) "
                "ON DUPLICATE KEY UPDATE setting_value = %s",
                (theme, theme)
            )
            connection.commit()
        except mysql.connector.Error as err:
            # If table doesn't exist, create it
            if err.errno == 1146:  # "Table doesn't exist" error
                try:
                    # Create the site_settings table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_settings` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `setting_key` varchar(255) NOT NULL UNIQUE,
                      `setting_value` text NOT NULL,
                      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    
                    # Insert the theme
                    cursor.execute(
                        "INSERT INTO site_settings (setting_key, setting_value) VALUES ('color_theme', %s)",
                        (theme,)
                    )
                    connection.commit()
                except Exception as create_err:
                    print(f"Error creating site_settings table: {create_err}")
                    return jsonify({"success": False, "error": str(create_err)}), 500
            else:
                print(f"Database error: {err}")
                return jsonify({"success": False, "error": str(err)}), 500
        
        cursor.close()
        connection.close()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Save theme error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Ensure password reset table exists
def create_password_reset_table():
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'password_reset_tokens'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating password_reset_tokens table...")
            
            # Create the table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry DATETIME NOT NULL,
                used TINYINT(1) DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Add index
            cursor.execute("CREATE INDEX idx_token ON password_reset_tokens(token)")
            
            connection.commit()
            print("Table created successfully")
        else:
            print("password_reset_tokens table already exists")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return False

if __name__ == '__main__':
    # Create password reset table if it doesn't exist
    create_password_reset_table()
    app.run(debug=True, host='127.0.0.1', port=8000)