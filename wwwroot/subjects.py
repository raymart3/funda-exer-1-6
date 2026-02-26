#subjects.py

import cgi
import mysql.connector
import html
import sys

print("Content-Type: text/html\n")
sys.stdout.flush()

form = cgi.FieldStorage()
action = form.getvalue("action", "")
selected_subjid = form.getvalue("selected_subjid", "")
studid = form.getvalue("studid", "")
tid = form.getvalue("tid", "")

subjid = form.getvalue("subjid", "")
subjcode = form.getvalue("subjcode", "")
subjdesc = form.getvalue("subjdesc", "")
subjunits = form.getvalue("subjunits", "")
subjsched = form.getvalue("subjsched", "")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="enrollmentsystem"
    )
    cursor = conn.cursor()

    if action == "insert" and subjcode and subjdesc:
        cursor.execute("SELECT IFNULL(MAX(subjid), 1999) + 1 FROM subjects")
        next_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO subjects (subjid, subjcode, subjdesc, subjunits, subjsched)
            VALUES (%s,%s,%s,%s,%s)
        """, (next_id, subjcode, subjdesc, subjunits, subjsched))
        conn.commit()
        selected_subjid = ""

    elif action == "update" and subjid and subjcode and subjdesc:
        cursor.execute("""
            UPDATE subjects
            SET subjcode=%s, subjdesc=%s, subjunits=%s, subjsched=%s
            WHERE subjid=%s
        """, (subjcode, subjdesc, subjunits, subjsched, subjid))
        conn.commit()

    elif action == "delete" and subjid:
        cursor.execute("DELETE FROM subjects WHERE subjid=%s", (subjid,))
        conn.commit()
        selected_subjid = ""
        subjid = ""
        subjcode = ""
        subjdesc = ""
        subjunits = ""
        subjsched = ""

    cursor.execute("SELECT IFNULL(MAX(subjid), 1999) + 1 FROM subjects")
    next_subjid = cursor.fetchone()[0]
    
    if selected_subjid and not action:
        cursor.execute("""
            SELECT subjid, subjcode, subjdesc, subjunits, subjsched
            FROM subjects WHERE subjid = %s
        """, (selected_subjid,))
        subject_row = cursor.fetchone()
        if subject_row:
            subjid = str(subject_row[0])
            subjcode = subject_row[1] or ""
            subjdesc = subject_row[2] or ""
            subjunits = str(subject_row[3]) if subject_row[3] else ""
            subjsched = subject_row[4] or ""

    cursor.execute("""
        SELECT subjid, subjcode, subjdesc, subjunits, subjsched
        FROM subjects
        ORDER BY subjid
    """)
    rows = cursor.fetchall()

    enrollment_counts = {}
    cursor.execute("""
        SELECT subjid, COUNT(*) as enrolled_count
        FROM enroll
        GROUP BY subjid
    """)
    enrollment_data = cursor.fetchall()
    for subject_id, count in enrollment_data:
        enrollment_counts[subject_id] = count

    enrolled_students = []
    subject_info = {}
    if selected_subjid:
        cursor.execute("""
            SELECT subjid, subjcode, subjdesc 
            FROM subjects 
            WHERE subjid = %s
        """, (selected_subjid,))
        subject_row = cursor.fetchone()
        if subject_row:
            subject_info = {'id': subject_row[0], 'code': subject_row[1], 'desc': subject_row[2]}
        
        cursor.execute("""
            SELECT s.studid, s.studname, s.studadd, s.studcrs, s.studgender, s.yrlvl
            FROM students s
            INNER JOIN enroll e ON s.studid = e.studid
            WHERE e.subjid = %s
            ORDER BY s.studname
        """, (selected_subjid,))
        enrolled_students = cursor.fetchall()

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
<a href="students.py{'?subjid_url=' + str(selected_subjid) if selected_subjid else ''}">Students</a>
<span>Subjects</span>
<a href="teachers.py{'?subjid_url=' + str(selected_subjid) if selected_subjid else ''}">Teachers</a>
<select name="createdbcombo" id="createdbcombo">
<option value="createdb">Create DB</option>
</select>
</td>
</tr>
<tr>
<td width="30%" valign="top">
<h3>Subject Form</h3>
<form action="subjects.py" method="post">
Subject ID:<br>
<input type="text" name="subjid" id="subjid" value="{subjid}" readonly><br>
Subject Code:<br>
<input type="text" name="subjcode" id="subjcode" value="{subjcode}"><br>
Description:<br>
<input type="text" name="subjdesc" id="subjdesc" value="{subjdesc}"><br><br>
Units:<br>
<input type="number" name="subjunits" id="subjunits" value="{subjunits}"><br><br>
Schedule:<br>
<input type="text" name="subjsched" id="subjsched" value="{subjsched}"><br><br>
<input type="hidden" name="action" id="action">
<input type="submit" value="Insert" onclick="document.getElementById('action').value='insert'">
<input type="submit" value="Update" onclick="document.getElementById('action').value='update'">
<input type="submit" value="Delete" onclick="document.getElementById('action').value='delete'">
""")
    
    if studid and not subjid:
        print(f'<input type="hidden" name="studid" value="{studid}">')
        print(f'<input type="submit" value="Enroll Student ID: {studid} to Subject ID: ?" onclick="document.getElementById(\'action\').value=\'enroll\'">')
    
    if tid and not subjid:
        print(f'<input type="hidden" name="tid" value="{tid}">')
        print(f'<input type="submit" value="Assign Teacher ID: {tid} to Subject ID: ?" onclick="document.getElementById(\'action\').value=\'assign\'">')
    
    print("""
</form>
</td>
<td width="70%" valign="top">
<h3>Subjects Table for: """+conn.database+"""</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr>
<th>ID</th>
<th>Code</th>
<th>Description</th>
<th>Units</th>
<th>Schedule</th>
<th>Enrolled Students</th>
</tr>
""")

    for i in range(len(rows)):
        id_val = str(rows[i][0])
        code_val = html.escape(str(rows[i][1]))
        desc_val = html.escape(str(rows[i][2] or ''))
        units_val = html.escape(str(rows[i][3] or ''))
        sched_val = html.escape(str(rows[i][4] or ''))
        enrolled_count = enrollment_counts.get(int(id_val), 0)
        
        row_class = 'class="selected"' if id_val == selected_subjid else ''
        
        url_params = f'selected_subjid={id_val}'
        if studid:
            url_params += f'&studid={studid}'
        if tid:
            url_params += f'&tid={tid}'
        print(f'<tr onclick="window.location.href=\'subjects.py?{url_params}\'" style="cursor:pointer;" {row_class}>')
        print(f"<td>{id_val}</td>")
        print(f"<td>{code_val}</td>")
        print(f"<td>{desc_val}</td>")
        print(f"<td>{units_val}</td>")
        print(f"<td>{sched_val}</td>")
        print(f"<td>{enrolled_count}</td>")
        print("</tr>")

    print("""
</table>
</td>
</tr>
<tr>
<td width="30%"></td>
<td width="70%" valign="top">
<h3>Enrolled Students</h3>
""")

    if selected_subjid and subject_info and 'id' in subject_info:
        print(f"""
<p>Subject: {html.escape(subject_info['code'])} - {html.escape(subject_info['desc'])}</p>
""")
        
        if enrolled_students:
            print("""
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr>
<th>Student ID</th>
<th>Name</th>
<th>Address</th>
<th>Course</th>
<th>Gender</th>
<th>Year Level</th>
</tr>
""")
            
            for j in range(len(enrolled_students)):
                stud_id = str(enrolled_students[j][0])
                stud_name = html.escape(str(enrolled_students[j][1] or ''))
                stud_add = html.escape(str(enrolled_students[j][2] or ''))
                stud_crs = html.escape(str(enrolled_students[j][3] or ''))
                stud_gen = html.escape(str(enrolled_students[j][4] or ''))
                stud_yr = html.escape(str(enrolled_students[j][5] or ''))
                
                print(f"<tr style=\"cursor:pointer;\">")
                print(f"<td>{stud_id}</td>")
                print(f"<td>{stud_name}</td>")
                print(f"<td>{stud_add}</td>")
                print(f"<td>{stud_crs}</td>")
                print(f"<td>{stud_gen}</td>")
                print(f"<td>{stud_yr}</td>")
                print("</tr>")
            
            print("""
</table>
""")
        else:
            print(f'<p>No students enrolled yet.</p>')

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
