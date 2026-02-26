#students.py

import cgi
import mysql.connector
import html
import sys

print("Content-Type: text/html\n")
sys.stdout.flush()

form = cgi.FieldStorage()
action = form.getvalue("action", "")
subjid = form.getvalue("subjid", "")
selected_subject = form.getvalue("selected_subject", "")

studid = form.getvalue("studid", "")
studname = form.getvalue("studname", "")
studadd = form.getvalue("studadd", "")
studcrs = form.getvalue("studcrs", "")
studgender = form.getvalue("studgender", "")
yrlvl = form.getvalue("yrlvl", "")

url_subjid = form.getvalue("subjid_url", "")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="enrollmentsystem"
    )
    cursor = conn.cursor()

    if action == "insert" and studname:
        cursor.execute("SELECT IFNULL(MAX(studid), 999) + 1 FROM students")
        next_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO students (studid, studname, studadd, studcrs, studgender, yrlvl)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (next_id, studname, studadd, studcrs, studgender, yrlvl))
        conn.commit()

    elif action == "update" and studid and studname:
        cursor.execute("""
            UPDATE students
            SET studname=%s, studadd=%s, studcrs=%s, studgender=%s, yrlvl=%s
            WHERE studid=%s
        """, (studname, studadd, studcrs, studgender, yrlvl, studid))
        conn.commit()

    elif action == "delete" and studid:
        cursor.execute("DELETE FROM students WHERE studid=%s", (studid,))
        conn.commit()
        studid = ""
        studname = ""
        studadd = ""
        studcrs = ""
        studgender = ""
        yrlvl = ""

    elif action == "enroll" and studid and subjid:
        try:
            result_args = cursor.callproc('checkconflict', [int(studid), int(subjid), 0, 0])
            conflict_msg = result_args[3]
            
            if conflict_msg == "No conflict":
                cursor.execute("INSERT INTO enroll (studid, subjid) VALUES (%s, %s)", (studid, subjid))
                conn.commit()
        except mysql.connector.Error:
            pass

    elif action == "drop" and studid and selected_subject:
        cursor.execute("DELETE FROM enroll WHERE studid=%s AND subjid=%s", (studid, selected_subject))
        conn.commit()
        selected_subject = ""

    cursor.execute("SELECT IFNULL(MAX(studid), 999) + 1 FROM students")
    next_studid = cursor.fetchone()[0]
    
    if studid and not action:
        cursor.execute("""
            SELECT studid, studname, studadd, studcrs, studgender, yrlvl
            FROM students WHERE studid = %s
        """, (studid,))
        student_row = cursor.fetchone()
        if student_row:
            studid = str(student_row[0])
            studname = student_row[1]
            studadd = student_row[2] or ""
            studcrs = student_row[3] or ""
            studgender = student_row[4] or ""
            yrlvl = student_row[5] or ""

    subject_info = {}
    subject_exists = False
    if subjid or url_subjid:
        check_subjid = subjid or url_subjid
        cursor.execute("SELECT subjid, subjcode, subjdesc FROM subjects WHERE subjid = %s", (check_subjid,))
        subject_row = cursor.fetchone()
        if subject_row:
            subject_info = {'id': subject_row[0], 'code': subject_row[1], 'desc': subject_row[2]}
            subject_exists = True
        else:
            print(f"""
<html>
<body>
<h2>Error: Subject Not Found</h2>
<p>Subject ID {check_subjid} does not exist in the database.</p>
<p><a href="students.py">Back to Students</a></p>
</body>
</html>
""")
            conn.close()
            sys.exit()

    cursor.execute("""
        SELECT s.studid, s.studname, s.studadd, s.studcrs, s.studgender, s.yrlvl,
               COALESCE(SUM(sub.subjunits), 0) as total_units
        FROM students s
        LEFT JOIN enroll e ON s.studid = e.studid
        LEFT JOIN subjects sub ON e.subjid = sub.subjid
        GROUP BY s.studid, s.studname, s.studadd, s.studcrs, s.studgender, s.yrlvl
        ORDER BY s.studid
    """)
    rows = cursor.fetchall()

    is_enrolled = False
    conflict_message = ""
    if studid and (subjid or url_subjid):
        check_subjid = subjid or url_subjid
        cursor.execute("SELECT * FROM enroll WHERE studid=%s AND subjid=%s", (studid, check_subjid))
        is_enrolled = cursor.fetchone() is not None
        
        if not is_enrolled:
            try:
                result_args = cursor.callproc('checkconflict', [int(studid), int(check_subjid), 0, 0])
                conflict_msg = result_args[3]
                if conflict_msg != "No conflict":
                    conflict_message = conflict_msg
            except:
                pass

    is_subject_enrolled = False
    if studid and selected_subject:
        cursor.execute("SELECT * FROM enroll WHERE studid=%s AND subjid=%s", (studid, selected_subject))
        is_subject_enrolled = cursor.fetchone() is not None

    print(f"""
<html>
<head>
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
  padding: 10px 20px;
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
navigation {{
  background-color: white;
  padding: 10px 20px;
  border-bottom: 1px solid #ddd;
}}
nav a, nav span {{
  margin-right: 20px;
  text-decoration: none;
  color: #0a68f5;
}}
nav a:hover {{
  text-decoration: underline;
}}
nav span {{
  color: #333;
  font-weight: bold;
}}
select {{
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  padding: 5px;
}}
input[type="text"],
input[type="number"] {{
  background-color: #ffffff;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px;
  margin: 5px 0;
  width: 100%;
  border-radius: 3px;
}}
input[type="text"]:readonly {{
  background-color: #f0f0f0;
}}
input[type="submit"] {{
  background-color: #0a68f5;
  color: white;
  border: none;
  padding: 8px 15px;
  margin: 5px 5px 5px 0;
  cursor: pointer;
  border-radius: 3px;
}}
input[type="submit"]:hover {{
  background-color: #0856d0;
}}
table {{
  border-collapse: collapse;
  width: 100%;
  background-color: white;
  margin-top: 10px;
}}
th {{
  background-color: #0a68f5;
  color: white;
  padding: 12px;
  text-align: left;
  font-weight: bold;
  border: 1px solid #ddd;
}}
td {{
  padding: 10px 12px;
  border: 1px solid #ddd;
}}
tr:hover {{
  background-color: #f9f9f9;
}}
h3 {{
  color: #0a68f5;
  margin-top: 10px;
  margin-bottom: 10px;
}}
form {{
  background-color: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 10px;
}}
.container {{
  padding: 20px;
}}
</style>
</head>
<body>
<table width="100%" cellpadding="10">
<div class="header">
<img src="catgulp.jpg">
<div class="header-text">
<h1>STUDENT INFORMATION SYSTEM</h1>
<span>UNIVERSITY NAME</span>
</div>
</div>
<tr>
<td colspan="2" style="padding: 10px 5px;">
<span>Students</span>
<a href="subjects.py{'?selected_subjid=' + str(url_subjid) if url_subjid else ''}">Subjects</a>
<a href="teachers.py">Teachers</a>
<select name="createdbcombo" id="createdbcombo">
<option value="createdb">Create DB</option>
</select>
</td>
</tr>
<tr>
<td width="30%" valign="top">
<h3>Student Form</h3>
<form action="students.py" method="post">
Student ID:<br>
<input type="text" name="studid" id="studid" value="{studid}" readonly><br>
Student Name:<br>
<input type="text" name="studname" id="studname" value="{studname}"><br>
Student Address:<br>
<input type="text" name="studadd" id="studadd" value="{studadd}"><br><br>
Student Course:<br>
<input type="text" name="studcrs" id="studcrs" value="{studcrs}"><br><br>
Student Gender:<br>
<input type="text" name="studgender" id="studgender" value="{studgender}"><br><br>
Year Level:<br>
<input type="number" name="yrlvl" id="yrlvl" value="{yrlvl}"><br><br>
<input type="hidden" name="action" id="action">
<input type="hidden" name="subjid_url" value="{url_subjid}">
<input type="submit" value="Insert" onclick="document.getElementById('action').value='insert'">
<input type="submit" value="Update" onclick="document.getElementById('action').value='update'">
<input type="submit" value="Delete" onclick="document.getElementById('action').value='delete'">
""")
    
    if url_subjid and not studid:
        print(f'<input type="hidden" name="subjid" value="{url_subjid}">')
        print(f'<input type="submit" value="Enroll Student ID: ? to Subject ID: {url_subjid}" onclick="document.getElementById(\'action\').value=\'enroll\'">')
    
    if (subjid or url_subjid) and studid and not is_enrolled and not conflict_message:
        print(f'<input type="hidden" name="subjid" value="{subjid or url_subjid}">')
        print(f'<input type="submit" value="Enroll Student ID: {studid} to Subject ID: {subjid or url_subjid}" onclick="document.getElementById(\'action\').value=\'enroll\'">')
    
    if conflict_message:
        print(f'<p style="color:red;">{conflict_message}</p>')
    
    if selected_subject and studid and is_subject_enrolled:
        print(f'<input type="hidden" name="selected_subject" value="{selected_subject}">')
        print(f'<input type="submit" value="Drop Student ID: {studid} from Subject ID: {selected_subject}" onclick="document.getElementById(\'action\').value=\'drop\'">')
    
    print("""
</form>
</td>
<td width="70%" valign="top">
<h3>Students Table for: """+conn.database+"""</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr>
<th>ID</th>
<th>Name</th>
<th>Address</th>
<th>Course</th>
<th>Gender</th>
<th>Year</th>
<th>Total Units</th>
</tr>
""")

    for i in range(len(rows)):
        id_val = str(rows[i][0])
        name_val = html.escape(str(rows[i][1]))
        add_val = html.escape(str(rows[i][2] or ''))
        crs_val = html.escape(str(rows[i][3] or ''))
        gen_val = html.escape(str(rows[i][4] or ''))
        yr_val = html.escape(str(rows[i][5] or ''))
        units_val = str(rows[i][6])
        
        row_class = 'class="selected"' if id_val == studid else ''
        
        url_param = f'&subjid_url={url_subjid}' if url_subjid else ''
        print(f'<tr onclick="window.location.href=\'students.py?studid={id_val}{url_param}\'" style="cursor:pointer;" {row_class}>')
        print(f"<td>{id_val}</td>")
        print(f"<td>{name_val}</td>")
        print(f"<td>{add_val}</td>")
        print(f"<td>{crs_val}</td>")
        print(f"<td>{gen_val}</td>")
        print(f"<td>{yr_val}</td>")
        print(f"<td>{units_val}</td>")
        print("</tr>")

    print("""
</table>
</td>
</tr>
<tr>
<td width="30%"></td>
<td width="70%" valign="top">
<h3>Enrolled Subjects</h3>
""")

    if studid:
        cursor.execute("SELECT studname FROM students WHERE studid = %s", (studid,))
        student_name_row = cursor.fetchone()
        student_name = student_name_row[0] if student_name_row else ""
        
        cursor.execute("""
            SELECT s.subjid, s.subjcode, s.subjdesc, s.subjunits, s.subjsched
            FROM subjects s
            INNER JOIN enroll e ON s.subjid = e.subjid
            WHERE e.studid = %s
            ORDER BY s.subjcode
        """, (studid,))
        enrolled_subjects = cursor.fetchall()
        
        print(f"""
<p>Student: {html.escape(student_name)}</p>
""")
        
        if enrolled_subjects:
            print("""
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr>
<th>Subject ID</th>
<th>Code</th>
<th>Description</th>
<th>Units</th>
<th>Schedule</th>
</tr>
""")
            
            for j in range(len(enrolled_subjects)):
                subj_id = str(enrolled_subjects[j][0])
                subj_code = html.escape(str(enrolled_subjects[j][1] or ''))
                subj_desc = html.escape(str(enrolled_subjects[j][2] or ''))
                subj_units = html.escape(str(enrolled_subjects[j][3] or ''))
                subj_sched = html.escape(str(enrolled_subjects[j][4] or ''))
                
                row_class = 'class="selected"' if subj_id == selected_subject else ''
                
                url_param = f'&subjid_url={url_subjid}' if url_subjid else ''
                print(f'<tr onclick="window.location.href=\'students.py?studid={studid}&selected_subject={subj_id}{url_param}\'" style="cursor:pointer;" {row_class}>')
                print(f"<td>{subj_id}</td>")
                print(f"<td>{subj_code}</td>")
                print(f"<td>{subj_desc}</td>")
                print(f"<td>{subj_units}</td>")
                print(f"<td>{subj_sched}</td>")
                print("</tr>")
            
            print("""
</table>
""")
        else:
            print(f'<p>No enrolled subjects yet.</p>')

    print("""
</td>
</tr>
</table>
</body>
</html>
""")

except Exception as e:
    print("<html><body>")
    print("<h2>Error</h2>")
    print("<pre>", html.escape(str(e)), "</pre>")
    print("</body></html>")

finally:
    if 'conn' in locals():
        conn.close()
