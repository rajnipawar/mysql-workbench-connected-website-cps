from flask import Flask, Blueprint, render_template, request, jsonify, flash, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '@Rppmysql18',  # Replace with your MySQL password
    'database': 'CPS_Database'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
analytics = Blueprint('analytics', __name__)
# Add to your app.py

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get quick stats
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM School) as school_count,
                (SELECT COUNT(*) FROM Students) as student_count,
                (SELECT COUNT(*) FROM Teachers) as teacher_count
            FROM DUAL
        """)
        stats = cursor.fetchone()

        # Get upcoming events
        cursor.execute("""
            SELECT 
                e.Event_id,
                e.Event_name,
                e.Event_date,
                e.Event_location,
                s.School_name
            FROM Events e
            JOIN School s ON e.School_id = s.School_id
            WHERE STR_TO_DATE(e.Event_date, '%m/%d/%Y') >= CURDATE()
            ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y')
            LIMIT 6
        """)
        events = cursor.fetchall()

        # Format dates for events
        for event in events:
            try:
                date_obj = datetime.strptime(event['Event_date'], '%m/%d/%Y')
                event['formatted_date'] = date_obj.strftime('%B %d, %Y')
            except (ValueError, TypeError):
                event['formatted_date'] = 'Date TBA'

        return render_template('index.html', stats=stats, events=events)

    except Error as e:
        print(f"Database error: {str(e)}")  # For debugging
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('index.html', stats={}, events=[])
    finally:
        if conn:
            conn.close()

@app.route('/schools')
def schools():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.*, 
                    COUNT(DISTINCT st.Student_id) as student_count,
                    COUNT(DISTINCT t.Teacher_id) as teacher_count
                FROM School s
                LEFT JOIN Students st ON s.School_id = st.School_id
                LEFT JOIN Teachers t ON s.School_id = t.School_id
                GROUP BY s.School_id
            """)
            schools = cursor.fetchall()
            return render_template('schools.html', schools=schools)
        except Error as e:
            flash(f"Database error: {str(e)}", 'error')
        finally:
            conn.close()
    return render_template('schools.html', schools=[])

@app.route('/teachers')
def teachers():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, 
                    s.School_name,
                    GROUP_CONCAT(DISTINCT sub.Subject_name) as subjects
                FROM Teachers t
                JOIN School s ON t.School_id = s.School_id
                LEFT JOIN Subjects sub ON t.Teacher_id = sub.Teacher_id
                GROUP BY t.Teacher_id
            """)
            teachers = cursor.fetchall()
            return render_template('teachers.html', teachers=teachers)
        except Error as e:
            flash(f"Database error: {str(e)}", 'error')
        finally:
            conn.close()
    return render_template('teachers.html', teachers=[])

@app.route('/facilities')
def facilities():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT f.*, s.School_name
                FROM Facility f
                JOIN School s ON f.School_id = s.School_id
                ORDER BY s.School_name, f.Facility_type
            """)
            facilities = cursor.fetchall()
            return render_template('facilities.html', facilities=facilities)
        except Error as e:
            flash(f"Database error: {str(e)}", 'error')
        finally:
            conn.close()
    return render_template('facilities.html', facilities=[])

# @app.route('/events')
# def events():
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor(dictionary=True)
        
#         # Get schools for dropdown
#         cursor.execute("SELECT School_id, School_name FROM School ORDER BY School_name")
#         schools = cursor.fetchall()
        
#         # Get filter parameters
#         school_id = request.args.get('school', 'all')
        
#         # Base query
#         base_query = """
#             SELECT 
#                 e.Event_id,
#                 e.Event_name,
#                 e.Event_date,
#                 e.Event_location,
#                 s.School_name,
#                 s.School_id
#             FROM Events e
#             JOIN School s ON e.School_id = s.School_id
#             WHERE 1=1
#         """

#         params = []
#         if school_id != 'all':
#             base_query += " AND e.School_id = %s"
#             params.append(school_id)

#         # Get upcoming events
#         upcoming_query = base_query + """ 
#             AND STR_TO_DATE(e.Event_date, '%m/%d/%Y') >= CURDATE() 
#             ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y') ASC
#         """
#         cursor.execute(upcoming_query, params)
#         upcoming_events = cursor.fetchall()

#         # Get past events (limited to 10)
#         past_query = base_query + """ 
#             AND STR_TO_DATE(e.Event_date, '%m/%d/%Y') < CURDATE() 
#             ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y') DESC 
#             LIMIT 10
#         """
#         cursor.execute(past_query, params)
#         past_events = cursor.fetchall()

#         # Format dates for all events
#         def format_date(events):
#             for event in events:
#                 try:
#                     date_obj = datetime.strptime(event['Event_date'], '%m/%d/%Y')
#                     event['formatted_date'] = date_obj.strftime('%B %d, %Y')
#                     event['formatted_time'] = date_obj.strftime('%I:%M %p')
#                 except (ValueError, TypeError):
#                     event['formatted_date'] = 'Date TBA'
#                     event['formatted_time'] = 'Time TBA'
#             return events

#         upcoming_events = format_date(upcoming_events)
#         past_events = format_date(past_events)

#         # Get counts
#         cursor.execute("""
#             SELECT 
#                 COUNT(CASE WHEN STR_TO_DATE(Event_date, '%m/%d/%Y') >= CURDATE() THEN 1 END) as upcoming_count,
#                 COUNT(CASE WHEN DATE(STR_TO_DATE(Event_date, '%m/%d/%Y')) = CURDATE() THEN 1 END) as today_count,
#                 COUNT(CASE WHEN STR_TO_DATE(Event_date, '%m/%d/%Y') < CURDATE() THEN 1 END) as past_count,
#                 COUNT(DISTINCT School_id) as school_count
#             FROM Events
#         """)
#         counts = cursor.fetchone()

#         return render_template('events.html',
#                              schools=schools,
#                              upcoming_events=upcoming_events,
#                              past_events=past_events,
#                              selected_school=school_id,
#                              upcoming_count=counts['upcoming_count'] or 0,
#                              today_count=counts['today_count'] or 0,
#                              past_count=counts['past_count'] or 0,
#                              school_count=counts['school_count'] or 0)

#     except Error as e:
#         print(f"Database error: {str(e)}")  # For debugging
#         flash(f"An error occurred: {str(e)}", "error")
#         return render_template('events.html', 
#                              schools=[], 
#                              upcoming_events=[], 
#                              past_events=[],
#                              upcoming_count=0,
#                              today_count=0,
#                              past_count=0,
#                              school_count=0)
#     finally:
#         if conn:
#             conn.close()

@app.route('/events')
def events():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get filter parameters
        school_id = request.args.get('school', 'all')
        event_type = request.args.get('type', 'upcoming')  # upcoming, past, or all
        search_query = request.args.get('search', '')
        
        # Get schools for dropdown
        cursor.execute("SELECT School_id, School_name FROM School ORDER BY School_name")
        schools = cursor.fetchall()
        
        # Base query with search
        base_query = """
            SELECT
                e.Event_id,
                e.Event_name,
                e.Event_date,
                e.Event_location,
                s.School_name,
                s.School_id
            FROM Events e
            JOIN School s ON e.School_id = s.School_id
            WHERE 1=1
        """
        params = []
        
        # Add school filter
        if school_id != 'all':
            base_query += " AND e.School_id = %s"
            params.append(school_id)
            
        # Add search filter
        if search_query:
            base_query += """ AND (
                e.Event_name LIKE %s OR 
                e.Event_location LIKE %s OR 
                s.School_name LIKE %s
            )"""
            search_param = f'%{search_query}%'
            params.extend([search_param, search_param, search_param])
        
        # Add date filter based on event_type
        if event_type == 'upcoming':
            base_query += " AND STR_TO_DATE(e.Event_date, '%m/%d/%Y') >= CURDATE()"
            order_by = "ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y') ASC"
        elif event_type == 'past':
            base_query += " AND STR_TO_DATE(e.Event_date, '%m/%d/%Y') < CURDATE()"
            order_by = "ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y') DESC"
        else:  # 'all' events
            order_by = "ORDER BY STR_TO_DATE(e.Event_date, '%m/%d/%Y') DESC"
            
        # Complete query with ordering
        final_query = f"{base_query} {order_by}"
        
        # Execute query
        cursor.execute(final_query, params)
        events = cursor.fetchall()
        
        # Format dates for all events
        def format_date(events):
            for event in events:
                try:
                    date_obj = datetime.strptime(event['Event_date'], '%m/%d/%Y')
                    event['formatted_date'] = date_obj.strftime('%B %d, %Y')
                    event['formatted_time'] = date_obj.strftime('%I:%M %p')
                    # Add a status field for display
                    current_date = datetime.now()
                    event_date = datetime.strptime(event['Event_date'], '%m/%d/%Y')
                    if event_date.date() == current_date.date():
                        event['status'] = 'Today'
                    elif event_date > current_date:
                        event['status'] = 'Upcoming'
                    else:
                        event['status'] = 'Past'
                except (ValueError, TypeError):
                    event['formatted_date'] = 'Date TBA'
                    event['formatted_time'] = 'Time TBA'
                    event['status'] = 'TBA'
            return events
            
        events = format_date(events)
        
        # Get counts for dashboard
        count_query = """
            SELECT
                COUNT(CASE WHEN STR_TO_DATE(Event_date, '%m/%d/%Y') >= CURDATE() THEN 1 END) as upcoming_count,
                COUNT(CASE WHEN DATE(STR_TO_DATE(Event_date, '%m/%d/%Y')) = CURDATE() THEN 1 END) as today_count,
                COUNT(CASE WHEN STR_TO_DATE(Event_date, '%m/%d/%Y') < CURDATE() THEN 1 END) as past_count,
                COUNT(DISTINCT School_id) as school_count
            FROM Events
        """
        cursor.execute(count_query)
        counts = cursor.fetchone()
        
        return render_template('events.html',
                             schools=schools,
                             events=events,
                             selected_school=school_id,
                             selected_type=event_type,
                             search_query=search_query,
                             upcoming_count=counts['upcoming_count'] or 0,
                             today_count=counts['today_count'] or 0,
                             past_count=counts['past_count'] or 0,
                             school_count=counts['school_count'] or 0)
                             
    except Error as e:
        print(f"Database error: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('events.html',
                             schools=[],
                             events=[],
                             upcoming_count=0,
                             today_count=0,
                             past_count=0,
                             school_count=0)
    finally:
        if conn:
            conn.close()

# Helper function to convert date string to datetime object
def parse_date(date_string):
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%m/%d/%Y')
    except ValueError:
        return None

# Helper function to get readable date format
def get_formatted_date(date_obj):
    if not date_obj:
        return 'Date TBA'
    return date_obj.strftime('%B %d, %Y')

# Helper function to check if an event is upcoming
def is_upcoming_event(date_string):
    date_obj = parse_date(date_string)
    if not date_obj:
        return False
    return date_obj.date() >= datetime.now().date()

# @app.route('/students')
# def students():
#     conn = get_db_connection()
#     if conn:
#         try:
#             cursor = conn.cursor(dictionary=True)
#             cursor.execute("""
#                 SELECT 
#                     s.Student_id,
#                     s.Student_name,
#                     s.Student_age,
                 
#                     sc.School_name,
#                     cl.Grade as class_grade,
#                     COALESCE(AVG(g.Grade_value), 0) as average_grade
#                 FROM Students s
#                 JOIN School sc ON s.School_id = sc.School_id
#                 JOIN Class_level cl ON s.Class_id = cl.Class_id
#                 LEFT JOIN Grades g ON s.Student_id = g.Student_id
#                 GROUP BY s.Student_id, s.Student_name, s.Student_age, sc.School_name, cl.Grade
#                 ORDER BY sc.School_name, s.Student_name
#             """)
#             students = cursor.fetchall()
#             return render_template('students.html', students=students)
#         except Error as e:
#             flash(f"Database error: {str(e)}", 'error')
#         finally:
#             conn.close()
#     return render_template('students.html', students=[])

@app.route('/students', methods=['GET', 'POST', 'DELETE'])
def students():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        msg = None
        
        # Get schools for dropdown
        cursor.execute("SELECT School_id, School_name FROM School ORDER BY School_name")
        schools = cursor.fetchall()
        
        # Handle POST request for add/update student
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add':
                # Add new student
                cursor.execute("""
                    INSERT INTO Students (Student_name, Student_age, School_id, Class_id)
                    VALUES (%s, %s, %s, %s)
                """, (
                    request.form.get('student_name'),
                    request.form.get('student_age'),
                    request.form.get('school_id'),
                    request.form.get('class_id')
                ))
                conn.commit()
                flash('Student added successfully!', 'success')
                
            elif action == 'update':
                # Update existing student
                cursor.execute("""
                    UPDATE Students 
                    SET Student_name = %s,
                        Student_age = %s,
                        School_id = %s,
                        Class_id = %s
                    WHERE Student_id = %s
                """, (
                    request.form.get('student_name'),
                    request.form.get('student_age'),
                    request.form.get('school_id'),
                    request.form.get('class_id'),
                    request.form.get('student_id')
                ))
                conn.commit()
                flash('Student updated successfully!', 'success')
                
        
        # Handle DELETE request
            elif action == 'delete':
                student_id = request.form.get('student_id')
                cursor.execute("DELETE FROM Students WHERE Student_id = %s", (student_id,))
                conn.commit()
                flash('Student deleted successfully!', 'success')
        
        # Get filter parameters
        search = request.args.get('search', '')
        school_id = request.args.get('school', 'all')
        
        # Base query
        query = """
            SELECT 
                s.Student_id,
                s.Student_name,
                s.Student_age,
                sch.School_name,
                cl.Grade as class_grade,
                ROUND(AVG(g.Grade_value), 1) as average_grade
            FROM Students s
            JOIN School sch ON s.School_id = sch.School_id
            JOIN Class_level cl ON s.Class_id = cl.Class_id
            LEFT JOIN Grades g ON s.Student_id = g.Student_id
            WHERE 1=1
        """
        params = []
        
        # Add search filter
        if search:
            query += " AND (s.Student_name LIKE %s OR sch.School_name LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        # Add school filter
        if school_id != 'all':
            query += " AND s.School_id = %s"
            params.append(school_id)
        
        query += " GROUP BY s.Student_id, s.Student_name, s.Student_age, sch.School_name, cl.Grade ORDER BY s.Student_name"
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        
        # Get class levels for dropdown
        cursor.execute("SELECT Class_id, Grade FROM Class_level ORDER BY Grade")
        classes = cursor.fetchall()
        
        return render_template('students.html',
                             students=students,
                             schools=schools,
                             classes=classes,
                             selected_school=school_id,
                             search_query=search)
                             
    except Error as e:
        print(f"Database error: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('students.html',
                             students=[],
                             schools=[],
                             classes=[])
    finally:
        if conn:
            conn.close()

@app.route('/basic-analytics')
def basic_analytics():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        data = {}

        # 1. School-wise Student Count and Average Age
        cursor.execute("""
            SELECT 
                s.School_name,
                COUNT(st.Student_id) as student_count,
                ROUND(AVG(IFNULL(st.Student_age, 0)), 1) as avg_age
            FROM School s 
            LEFT JOIN Students st ON s.School_id = st.School_id
            GROUP BY s.School_name
            ORDER BY student_count DESC
        """)
        data['school_stats'] = cursor.fetchall()

        # # 2. Grade Distribution by Class
        # cursor.execute("""
        #     SELECT 
        #         c.Grade as class_grade,
        #         COUNT(DISTINCT s.Student_id) as student_count,
        #         COUNT(DISTINCT t.Teacher_id) as teacher_count,
        #         COUNT(DISTINCT sub.Subject_id) as subject_count,
        #         ROUND(AVG(IFNULL(g.Grade_value, 0)), 2) as avg_grade
        #     FROM Class_level c
        #     LEFT JOIN Students s ON c.Class_id = s.Class_id
        #     LEFT JOIN Teachers t ON c.Teacher_id = t.Teacher_id
        #     LEFT JOIN Subjects sub ON c.Class_id = sub.Class_id
        #     LEFT JOIN Grades g ON s.Student_id = g.Student_id
        #     GROUP BY c.Grade
        #     ORDER BY c.Grade
        # """)
        # data['grade_stats'] = cursor.fetchall()

        # # 3. Fixed Subject Performance Query
        # cursor.execute("""
        #     SELECT 
        #         s.Subject_name,
        #         COUNT(DISTINCT st.Student_id) as enrolled_students,
        #         COUNT(DISTINCT t.Teacher_id) as teachers_count,
        #         CASE 
        #             WHEN COUNT(g.Grade_value) > 0 THEN ROUND(AVG(g.Grade_value), 2)
        #             ELSE NULL
        #         END as avg_grade
        #     FROM Subjects s
        #     LEFT JOIN Class_level cl ON s.Class_id = cl.Class_id
        #     LEFT JOIN Students st ON cl.Class_id = st.Class_id
        #     LEFT JOIN Teachers t ON s.Teacher_id = t.Teacher_id
        #     LEFT JOIN Grades g ON st.Student_id = g.Student_id
        #     GROUP BY s.Subject_name
        #     ORDER BY avg_grade IS NULL, avg_grade DESC
        # """)
        # data['subject_stats'] = cursor.fetchall()

        cursor.execute("""
            SELECT 
                s.School_name,
                f.Facility_type,
                COUNT(f.Facility_id) as facility_count,
                SUM(f.Facility_capacity) as total_capacity,
                ROUND(AVG(f.Facility_capacity), 2) as avg_capacity
            FROM School s
            JOIN Facility f ON s.School_id = f.School_id
            GROUP BY s.School_name, f.Facility_type
            ORDER BY s.School_name, facility_count DESC
        """)
        data['facility_utilization'] = cursor.fetchall()

        cursor.execute("""
            SELECT 
                s.School_name,
                COUNT(e.Event_id) as event_count,
                ROUND(AVG(
                    (SELECT COUNT(DISTINCT st.Student_id) 
                    FROM Students st 
                    WHERE st.School_id = s.School_id)
                ), 2) as avg_student_count
            FROM School s
            LEFT JOIN Events e ON s.School_id = e.School_id
            GROUP BY s.School_id, s.School_name
            ORDER BY event_count DESC
        """)
        data['event_participation'] = cursor.fetchall()
    

        return render_template('basic_analytics.html', data=data)

    except Error as e:
        print(f"Database error: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('basic_analytics.html', data={})
    finally:
        if conn:
            conn.close()

@app.route('/advanced-analytics', methods=['GET', 'POST'])
def advanced_analytics():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        data = {}
        
        school_id = request.args.get('school', 'all')
        limit = int(request.args.get('limit', '5'))  # Convert to integer with default 5
        
        # Get schools for dropdown
        cursor.execute("SELECT School_id, School_name FROM School ORDER BY School_name")
        schools = cursor.fetchall()

        # 1. Top Performing Students Analysis
        student_query = """
            WITH StudentGrades AS (
                SELECT 
                    st.Student_id,
                    st.Student_name,
                    st.Student_age,
                    s.School_name,
                    cl.Grade,
                    ROUND(AVG(g.Grade_value), 2) as avg_grade,
                    COUNT(DISTINCT sub.Subject_id) as subjects_taken
                FROM Students st
                JOIN School s ON st.School_id = s.School_id
                JOIN Class_level cl ON st.Class_id = cl.Class_id
                JOIN Grades g ON st.Student_id = g.Student_id
                JOIN Subjects sub ON g.Class_id = sub.Class_id
                WHERE g.Grade_value IS NOT NULL
                {school_filter}
                GROUP BY st.Student_id, st.Student_name, st.Student_age, s.School_name, cl.Grade
            )
            SELECT 
                Student_name,
                School_name,
                Grade,
                avg_grade,
                subjects_taken,
                CASE 
                    WHEN avg_grade >= 90 THEN 'Outstanding'
                    WHEN avg_grade >= 80 THEN 'Excellent'
                    WHEN avg_grade >= 70 THEN 'Good'
                    ELSE 'Needs Improvement'
                END as performance_level
            FROM StudentGrades
            ORDER BY avg_grade DESC
            LIMIT %s
        """
        
        # Add school filter if specified
        school_filter = "AND st.School_id = %s" if school_id != 'all' else ""
        query_params = [limit] if school_id == 'all' else [school_id, limit]
        
        # Execute query with parameters
        formatted_query = student_query.format(school_filter=school_filter)
        cursor.execute(formatted_query, query_params)
        data['top_students'] = cursor.fetchall()

        # 2. Comprehensive Event Analysis with comparative metrics
        event_query = """
            WITH EventStats AS (
                SELECT 
                    e.Event_name,
                    e.Event_date,
                    e.Event_location,
                    s.School_name,
                    MONTH(STR_TO_DATE(e.Event_date, '%m/%d/%Y')) as event_month,
                    COUNT(*) OVER (PARTITION BY s.School_id) as school_event_count,
                    COUNT(*) OVER (PARTITION BY MONTH(STR_TO_DATE(e.Event_date, '%m/%d/%Y'))) as month_event_count
                FROM Events e
                JOIN School s ON e.School_id = s.School_id
                WHERE STR_TO_DATE(e.Event_date, '%m/%d/%Y') 
                {school_filter}
            )
            SELECT 
                Event_name,
                Event_date,
                Event_location,
                School_name,
                school_event_count,
                month_event_count,
                DENSE_RANK() OVER (ORDER BY STR_TO_DATE(Event_date, '%m/%d/%Y')) as chronological_rank
            FROM EventStats
            ORDER BY STR_TO_DATE(Event_date, '%m/%d/%Y') ASC
            LIMIT %s
        """
        
        # Properly handle school filter and parameters for events
        if school_id != 'all':
            school_filter = "AND e.School_id = %s"
            formatted_event_query = event_query.format(school_filter=school_filter)
            cursor.execute(formatted_event_query, [school_id, int(limit)])  # Ensure limit is explicitly converted to int
        else:
            school_filter = ""
            formatted_event_query = event_query.format(school_filter=school_filter)
            cursor.execute(formatted_event_query, [int(limit)])  # Ensure limit is explicitly converted to int
            
        event_data = cursor.fetchall()
        
        # Process event data
        data['event_analysis'] = []
        for event in event_data:
            formatted_event = dict(event)
            try:
                date_obj = datetime.strptime(event['Event_date'], '%m/%d/%Y')
                formatted_event['formatted_date'] = date_obj.strftime('%B %d, %Y')
            except ValueError:
                formatted_event['formatted_date'] = event['Event_date']
            data['event_analysis'].append(formatted_event)

        # 3. Teacher Performance and Workload Analysis
        teacher_query = """
            WITH TeacherMetrics AS (
                SELECT 
                    t.Teacher_id,
                    t.Teacher_name,
                    s.School_name,
                    COUNT(DISTINCT sub.Subject_id) as subjects_taught,
                    COUNT(DISTINCT st.Student_id) as total_students,
                    AVG(g.Grade_value) as class_avg_grade
                FROM Teachers t
                JOIN School s ON t.School_id = s.School_id
                LEFT JOIN Class_level cl ON t.Teacher_id = cl.Teacher_id
                LEFT JOIN Subjects sub ON t.Teacher_id = sub.Teacher_id
                LEFT JOIN Students st ON cl.Class_id = st.Class_id
                LEFT JOIN Grades g ON st.Student_id = g.Student_id
                GROUP BY t.Teacher_id, t.Teacher_name, s.School_name
            )
            SELECT 
                Teacher_name,
                School_name,
                subjects_taught,
                total_students,
                ROUND(class_avg_grade, 2) as class_avg_grade,
                CASE 
                    WHEN total_students > 100 THEN 'High'
                    WHEN total_students > 50 THEN 'Medium'
                    ELSE 'Low'
                END as workload_level,
                NTILE(4) OVER (ORDER BY class_avg_grade DESC) as performance_quartile
            FROM TeacherMetrics
            ORDER BY class_avg_grade DESC
            LIMIT %s
        """
        cursor.execute(teacher_query, [int(limit)])
        data['teacher_analysis'] = cursor.fetchall()
        # Add these to your route before returning the template
        data['top_students'] = format_performance_data(data['top_students'])
        data['event_analysis'] = [dict(item, **{'formatted_date': format_date(item['Event_date'])}) 
                                for item in data['event_analysis']]
        return render_template('advanced_analytics.html',
                             data=data,
                             schools=schools,
                             selected_school=school_id,
                             current_limit=limit)

    except Error as e:
        print(f"Database error: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('advanced_analytics.html', data={})
    finally:
        if conn:
            conn.close()

# Add these helper functions to your route file

def format_performance_data(data):
    """Format and enrich performance data"""
    for item in data:
        if 'avg_grade' in item and item['avg_grade']:
            item['avg_grade'] = float(item['avg_grade'])
            item['performance_color'] = get_performance_color(item['avg_grade'])
    return data

def get_performance_color(grade):
    """Get appropriate color class based on grade"""
    if grade >= 90:
        return 'green'
    elif grade >= 80:
        return 'blue'
    elif grade >= 70:
        return 'yellow'
    return 'red'

def format_date(date_str):
    """Format date string to readable format"""
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str


if __name__ == '__main__':
    app.run(debug=True)