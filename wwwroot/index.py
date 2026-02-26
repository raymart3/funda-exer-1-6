#!/usr/bin/env python3
# index.py - Login and Database Selection
import cgi
import mysql.connector
import html
import sys
import json

print("Content-Type: text/html\n")
sys.stdout.flush()

form = cgi.FieldStorage()
action = form.getvalue("action", "")
username = form.getvalue("username", "").strip()
password = form.getvalue("password", "").strip()
selected_semester = form.getvalue("semester", "1stsem_sy2026_2027").strip()

# Session variables (in a real application, use proper session management)
logged_in = False
current_user = None
current_semester = None
error_message = ""
success_message = ""

try:
    # Connect to MySQL server to check credentials
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="enrollmentsystem"
    )
    cursor = conn.cursor()
    
    if action == "login" and username and password:
        # Verify credentials - check for root/root
        if username == "root" and password == "root":
            logged_in = True
            current_user = username
            current_semester = selected_semester
            
            # Auto-create the first database if it doesn't exist
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{selected_semester}`")
                conn.commit()
            except mysql.connector.Error as db_err:
                error_message = f"Database error: {str(db_err)}"
            
            # Grant privileges using stored procedure if available
            if not error_message:
                try:
                    cursor.callproc('grant_user_privileges', 
                        [username, 'localhost', selected_semester, ''])
                    conn.commit()
                except:
                    pass  # Stored procedure may not exist yet, that's ok
            
            if not error_message:
                success_message = f"Login successful! Welcome, {username}"
        else:
            error_message = "Invalid username or password"
    
    elif action == "continue" and username and selected_semester:
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{selected_semester}`")
        conn.commit()
        
        # Grant privileges
        try:
            cursor.callproc('grant_user_privileges', 
                [username, 'localhost', selected_semester, ''])
            conn.commit()
        except:
            pass
        
        # Redirect to main page - semester is just for organization
        print(f"""
        <html>
        <head>
        <script>
        setTimeout(function() {{
            window.location.href = 'students.py?semester={html.escape(selected_semester)}&user={html.escape(username)}';
        }}, 500);
        </script>
        </head>
        <body>
        <p>Redirecting to Students page...</p>
        </body>
        </html>
        """)
        conn.close()
        sys.exit()
    
    conn.close()
    
except mysql.connector.Error as e:
    error_message = f"Database connection error: {str(e)}"

# Determine which page to show
show_login = True
show_semester_select = False

if action == "login" and logged_in:
    show_login = False
    show_semester_select = True

# Display appropriate page
if show_login:
    print(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Information System - Login</title>
    <style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    body {{
        background-color: #f5f5f5;
        color: #333;
        font-family: Arial, sans-serif;
    }}
    .header {{
        display: flex;
        align-items: center;
        padding: 15px 20px;
        background: #0a68f5;
        color: white;
    }}
    .header img {{
        height: 80px;
        width: 80px;
        margin-right: 15px;
    }}
    .header-text {{
        display: flex;
        flex-direction: column;
    }}
    .header-text h1 {{
        margin: 0;
        font-size: 24px;
    }}
    .header-text span {{
        font-size: 14px;
        opacity: 0.9;
    }}
    .container {{
        display: flex;
        padding: 40px 20px;
        gap: 40px;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .login-section {{
        flex: 0 0 300px;
    }}
    .welcome-section {{
        flex: 1;
    }}
    .login-section h2 {{
        font-size: 20px;
        margin-bottom: 20px;
        color: #0a68f5;
    }}
    .form-group {{
        margin-bottom: 15px;
    }}
    .form-group label {{
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }}
    .form-group input {{
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
    }}
    .form-group input:focus {{
        outline: none;
        border-color: #0a68f5;
        box-shadow: 0 0 5px rgba(10, 104, 245, 0.3);
    }}
    .button-group {{
        display: flex;
        gap: 10px;
    }}
    button {{
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
    }}
    .btn-login {{
        background-color: #0a68f5;
        color: white;
        flex: 1;
    }}
    .btn-login:hover {{
        background-color: #0553d4;
    }}
    .welcome-section h1 {{
        font-size: 28px;
        color: #0a68f5;
        margin-bottom: 10px;
    }}
    .welcome-section p {{
        text-align: justify;
        line-height: 1.6;
        color: #666;
    }}
    .error-message {{
        background-color: #f8d7da;
        color: #721c24;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
        border: 1px solid #f5c6cb;
    }}
    .success-message {{
        background-color: #d4edda;
        color: #155724;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
        border: 1px solid #c3e6cb;
    }}
    </style>
    </head>
    <body>
    <div class="header">
    <img src="logo.png" alt="University Logo">
    <div class="header-text">
    <h1>STUDENT INFORMATION SYSTEM</h1>
    <span>UNIVERSITY NAME</span>
    </div>
    </div>
    <div class="container">
    <div class="login-section">
    <h2>Login</h2>
    {f'<div class="error-message">{html.escape(error_message)}</div>' if error_message else ''}
    {f'<div class="success-message">{html.escape(success_message)}</div>' if success_message else ''}
    <form method="POST" action="index.py">
    <div class="form-group">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required>
    </div>
    <div class="form-group">
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required>
    </div>
    <div class="button-group">
    <button type="submit" name="action" value="login" class="btn-login">Login</button>
    </div>
    </form>
    </div>
    <div class="welcome-section">
    <h1>Welcome to Student System</h1>
    <p>Please login to continue.</p>
    </div>
    </div>
    </body>
    </html>
    """)

elif show_semester_select:
    print(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Information System - Select Semester</title>
    <style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    body {{
        background-color: #f5f5f5;
        color: #333;
        font-family: Arial, sans-serif;
    }}
    .header {{
        display: flex;
        align-items: center;
        padding: 15px 20px;
        background: #0a68f5;
        color: white;
    }}
    .header img {{
        height: 80px;
        width: 80px;
        margin-right: 15px;
    }}
    .header-text {{
        display: flex;
        flex-direction: column;
    }}
    .header-text h1 {{
        margin: 0;
        font-size: 24px;
    }}
    .header-text span {{
        font-size: 14px;
        opacity: 0.9;
    }}
    .container {{
        display: flex;
        padding: 40px 20px;
        gap: 40px;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .semester-section {{
        flex: 0 0 300px;
    }}
    .welcome-section {{
        flex: 1;
    }}
    .semester-section h2 {{
        font-size: 20px;
        margin-bottom: 20px;
        color: #0a68f5;
    }}
    .form-group {{
        margin-bottom: 15px;
    }}
    .form-group label {{
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }}
    .form-group select {{
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
    }}
    .form-group select:focus {{
        outline: none;
        border-color: #0a68f5;
        box-shadow: 0 0 5px rgba(10, 104, 245, 0.3);
    }}
    .button-group {{
        display: flex;
        gap: 10px;
    }}
    button {{
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
    }}
    .btn-continue {{
        background-color: #0a68f5;
        color: white;
        flex: 1;
    }}
    .btn-continue:hover {{
        background-color: #0553d4;
    }}
    .welcome-section h1 {{
        font-size: 28px;
        color: #0a68f5;
        margin-bottom: 10px;
    }}
    .welcome-section p {{
        text-align: justify;
        line-height: 1.6;
        color: #666;
    }}
    .user-info {{
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-left: 4px solid #0a68f5;
    }}
    .user-info p {{
        margin: 5px 0;
        color: #0a68f5;
    }}
    </style>
    </head>
    <body>
    <div class="header">
    <img src="logo.png" alt="University Logo">
    <div class="header-text">
    <h1>STUDENT INFORMATION SYSTEM</h1>
    <span>UNIVERSITY NAME</span>
    </div>
    </div>
    <div class="container">
    <div class="semester-section">
    <h2>Select School Year</h2>
    {f'<div style="background-color: #d4edda; color: #155724; padding: 12px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #c3e6cb;">{html.escape(success_message)}</div>' if success_message else ''}
    <form method="POST" action="index.py">
    <input type="hidden" name="username" value="{html.escape(current_user)}">
    <div class="form-group">
    <label for="semester">School Year:</label>
    <select id="semester" name="semester" required>
    <option value="1stsem_sy2026_2027">1st Sem 2026-2027</option>
    <option value="2ndsem_sy2026_2027">2nd Sem 2026-2027</option>
    <option value="summer_sy2026_2027">Summer 2026-2027</option>
    </select>
    </div>
    <div class="button-group">
    <button type="submit" name="action" value="continue" class="btn-continue">Continue</button>
    </div>
    </form>
    </div>
    <div class="welcome-section">
    <h1>Welcome to Student System</h1>
    <p>Please select the school year/semester to continue. The database will be created automatically.</p>
    </div>
    </div>
    </body>
    </html>
    """)

sys.exit()
