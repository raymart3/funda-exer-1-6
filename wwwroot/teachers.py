#!C:/Python3.9/python.exe
#teachers.py

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

tid = form.getvalue("tid", "")
tname = form.getvalue("tname", "")
tdept = form.getvalue("tdept", "")
tadd = form.getvalue("tadd", "")
tcontact = form.getvalue("tcontact", "")
tstatus = form.getvalue("tstatus", "")

# Get URL parameters for context preservation
url_subjid = form.getvalue("subjid_url", "")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="enrollmentsystem"
    )
    cursor = conn.cursor()

    # INSERT
    if action == "insert" and tname:
        cursor.execute("SELECT IFNULL(MAX(tid), 2999) + 1 FROM teachers")
        next_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO teachers (tid, tname, tdept, tadd, tcontact, tstatus)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (next_id, tname, tdept, tadd, tcontact, tstatus))
        conn.commit()

    # UPDATE
    elif action == "update" and tid and tname:
        cursor.execute("""
            UPDATE teachers
            SET tname=%s, tdept=%s, tadd=%s, tcontact=%s, tstatus=%s
            WHERE tid=%s
        """, (tname, tdept, tadd, tcontact, tstatus, tid))
        conn.commit()

    # DELETE
    elif action == "delete" and tid:
        cursor.execute("DELETE FROM teachers WHERE tid=%s", (tid,))
        conn.commit()
        tid = ""
        tname = ""
        tdept = ""
        tadd = ""
        tcontact = ""
        tstatus = ""

    # ASSIGN TEACHER with conflict check
    elif action == "assign" and tid and subjid:
        try:
            # Call stored procedure to check for schedule conflicts
            result_args = cursor.callproc('checkconflict', [int(tid), int(subjid), 1, 0])
            conflict_msg = result_args[3]
            
            if conflict_msg == "No conflict":
                cursor.execute("INSERT INTO assign (subjid, tid) VALUES (%s, %s)", (subjid, tid))
                conn.commit()
        except mysql.connector.Error:
            pass  # Already assigned or conflict

    # UNASSIGN TEACHER
    elif action == "unassign" and tid and selected_subject:
        cursor.execute("DELETE FROM assign WHERE tid=%s AND subjid=%s", (tid, selected_subject))
        conn.commit()
        selected_subject = ""

    # NEXT TEACHER ID
    cursor.execute("SELECT IFNULL(MAX(tid), 2999) + 1 FROM teachers")
    next_tid = cursor.fetchone()[0]
    
    # Load teacher data if tid is in URL (for row clicks)
    if tid and not action:
        cursor.execute("""
            SELECT tid, tname, tdept, tadd, tcontact, tstatus
            FROM teachers WHERE tid = %s
        """, (tid,))
        teacher_row = cursor.fetchone()
        if teacher_row:
            tid = str(teacher_row[0])
            tname = teacher_row[1]
            tdept = teacher_row[2] or ""
            tadd = teacher_row[3] or ""
            tcontact = teacher_row[4] or ""
            tstatus = teacher_row[5] or ""

    # GET SUBJECT INFO IF PROVIDED
    subject_info = {}
    subject_exists = False
    if subjid or url_subjid:
        # Use url_subjid if subjid is not set (for context preservation)
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
<p><a href="teachers.py">Back to Teachers</a></p>
</body>
</html>
""")
            conn.close()
            sys.exit()

    # FETCH TEACHERS
    cursor.execute("""
        SELECT tid, tname, tdept, tadd, tcontact, tstatus
        FROM teachers
        ORDER BY tid
    """)
    rows = cursor.fetchall()

    # Check assignment status and conflict
    is_assigned = False
    conflict_message = ""
    if tid and (subjid or url_subjid):
        # Use url_subjid if subjid is not set (for context preservation)
        check_subjid = subjid or url_subjid
        cursor.execute("SELECT * FROM assign WHERE tid=%s AND subjid=%s", (tid, check_subjid))
        is_assigned = cursor.fetchone() is not None
        
        if not is_assigned:
            # Check for conflict
            try:
                result_args = cursor.callproc('checkconflict', [int(tid), int(check_subjid), 1, 0])
                conflict_msg = result_args[3]
                if conflict_msg != "No conflict":
                    conflict_message = conflict_msg
            except:
                pass

    # Check if selected subject is still assigned
    is_subject_assigned = False
    if tid and selected_subject:
        cursor.execute("SELECT * FROM assign WHERE tid=%s AND subjid=%s", (tid, selected_subject))
        is_subject_assigned = cursor.fetchone() is not None

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
<a href="students.py">Students</a>
<a href="subjects.py">Subjects</a>
<span>Teachers</span>
<select name="createdbcombo" id="createdbcombo">
<option value="createdb">Create DB</option>
</select>
</td>
</tr>
<tr>
<td width="30%" valign="top">
<h3>Teacher Form</h3>
<form action="teachers.py" method="post">
Teacher ID:<br>
<input type="text" name="tid" id="tid" value="{tid}" readonly><br>
Teacher Name:<br>
<input type="text" name="tname" id="tname" value="{tname}"><br>
Department:<br>
<input type="text" name="tdept" id="tdept" value="{tdept}"><br><br>
Address:<br>
<input type="text" name="tadd" id="tadd" value="{tadd}"><br><br>
Contact:<br>
<input type="text" name="tcontact" id="tcontact" value="{tcontact}"><br><br>
Status:<br>
<input type="text" name="tstatus" id="tstatus" value="{tstatus}"><br><br>
<input type="hidden" name="action" id="action">
<input type="hidden" name="subjid_url" value="{url_subjid}">
<input type="submit" value="Insert" onclick="document.getElementById('action').value='insert'">
<input type="submit" value="Update" onclick="document.getElementById('action').value='update'">
<input type="submit" value="Delete" onclick="document.getElementById('action').value='delete'">
""")
    
    # Show Assign button - only if coming from Subjects page with a subject selected
    if url_subjid and not tid:
        print(f'<input type="hidden" name="subjid" value="{url_subjid}">')
        print(f'<input type="submit" value="Assign Teacher ID: ? to Subject ID: {url_subjid}" onclick="document.getElementById(\'action\').value=\'assign\'">')
    
    # Show Assign button - when teacher is selected and subject is provided
    if (subjid or url_subjid) and tid and not is_assigned and not conflict_message:
        print(f'<input type="hidden" name="subjid" value="{subjid or url_subjid}">')
        print(f'<input type="submit" value="Assign Teacher ID: {tid} to Subject ID: {subjid or url_subjid}" onclick="document.getElementById(\'action\').value=\'assign\'">')
    
    # Show conflict message
    if conflict_message:
        print(f'<p style="color:red;">{conflict_message}</p>')
    
    # Show Unassign button
    if selected_subject and tid and is_subject_assigned:
        print(f'<input type="hidden" name="selected_subject" value="{selected_subject}">')
        print(f'<input type="submit" value="Unassign Teacher ID: {tid} from Subject ID: {selected_subject}" onclick="document.getElementById(\'action\').value=\'unassign\'">')
    
    print("""
</form>
</td>
<td width="70%" valign="top">
<h3>Teachers Table for: """+conn.database+"""</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr>
<th>ID</th>
<th>Name</th>
<th>Department</th>
<th>Address</th>
<th>Contact</th>
<th>Status</th>
</tr>
""")

    for i in range(len(rows)):
        id_val = str(rows[i][0])
        name_val = html.escape(str(rows[i][1]))
        dept_val = html.escape(str(rows[i][2] or ''))
        add_val = html.escape(str(rows[i][3] or ''))
        contact_val = html.escape(str(rows[i][4] or ''))
        status_val = html.escape(str(rows[i][5] or ''))
        
        row_class = 'class="selected"' if id_val == tid else ''
        
        url_params = f'tid={id_val}'
        if url_subjid:
            url_params += f'&subjid_url={url_subjid}'
        print(f'<tr onclick="window.location.href=\'teachers.py?{url_params}\'" style="cursor:pointer;" {row_class}>')
        print(f"<td>{id_val}</td>")
        print(f"<td>{name_val}</td>")
        print(f"<td>{dept_val}</td>")
        print(f"<td>{add_val}</td>")
        print(f"<td>{contact_val}</td>")
        print(f"<td>{status_val}</td>")
        print("</tr>")

    print("""
</table>
</td>
</tr>
<tr>
<td width="30%"></td>
<td width="70%" valign="top">
<h3>Assigned Subjects</h3>
""")

    # Show assigned subjects
    if tid:
        cursor.execute("SELECT tname FROM teachers WHERE tid = %s", (tid,))
        teacher_name_row = cursor.fetchone()
        teacher_name = teacher_name_row[0] if teacher_name_row else ""
        
        cursor.execute("""
            SELECT s.subjid, s.subjcode, s.subjdesc, s.subjunits, s.subjsched
            FROM subjects s
            INNER JOIN assign a ON s.subjid = a.subjid
            WHERE a.tid = %s
            ORDER BY s.subjcode
        """, (tid,))
        assigned_subjects = cursor.fetchall()
        
        print(f"""
<p>Teacher: {html.escape(teacher_name)}</p>
""")
        
        if assigned_subjects:
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
            
            for j in range(len(assigned_subjects)):
                subj_id = str(assigned_subjects[j][0])
                subj_code = html.escape(str(assigned_subjects[j][1] or ''))
                subj_desc = html.escape(str(assigned_subjects[j][2] or ''))
                subj_units = html.escape(str(assigned_subjects[j][3] or ''))
                subj_sched = html.escape(str(assigned_subjects[j][4] or ''))
                
                row_class = 'class="selected"' if subj_id == selected_subject else ''
                
                print(f'<tr onclick="window.location.href=\'teachers.py?tid={tid}&selected_subject={subj_id}\'" style="cursor:pointer;" {row_class}>')
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
            print(f'<p>No assigned subjects yet.</p>')

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
