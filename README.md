# Chicago Public Schools Dashboard

A comprehensive web application for managing and analyzing data from Chicago Public Schools. This application provides an intuitive interface for accessing information about schools, students, teachers, and facilities while offering basic and advanced analytics capabilities.

## Features

### Core Functionality
- **School Management**: View comprehensive school information including student and teacher counts
- **Student Directory**: 
  - View and manage student information
  - Add, update, and delete student records
  - Advanced filtering by school and search functionality
  - Track student grades and performance metrics
- **Teacher Directory**: Track teacher assignments, subjects, and school affiliations
- **Facility Management**: Monitor school facilities, capacities, and utilization
- **Event Management**:
  - Filter events by school and type (upcoming/past)
  - Search functionality for events
  - Track event locations and dates
  - View event statistics and counts

### Analytics Capabilities

#### Basic Analytics
- School-wise student distribution and average age analysis
- Facility utilization metrics by school and type
- Event participation statistics
- School performance indicators

#### Advanced Analytics
- Top performing students analysis with performance levels
- Comprehensive event analysis with comparative metrics
- Teacher performance and workload analysis including:
  - Subjects taught
  - Total students
  - Class average grades
  - Workload levels
  - Performance quartiles

## Project Structure

```
cps-dashboard/
│
├── app.py                 # Main application file with routes and database logic
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── static/               # Static files
│   ├── css/             # Stylesheets
│   │   └── main.css     # Main stylesheet
│   └── js/              # JavaScript files
│       └── main.js      # Main JavaScript functionality
│
└── templates/            # HTML templates
    ├── layout/
    │── base.html        # Base template
    ├── index.html       # Dashboard home page
    ├── schools.html     # Schools list and management
    ├── students.html    # Student directory and management
    ├── teachers.html    # Teacher directory
    ├── events.html      # Event calendar and management
    ├── facilities.html  # Facilities management
    ├── basic_analytics.html    # Basic analytics dashboard
    └── advanced_analytics.html # Advanced analytics dashboard



```

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML5, Tailwind CSS
- **Additional Libraries**: 
  - mysql-connector-python
  - datetime

## Database Schema

```sql
School (School_id, School_name, School_contact, School_address)
Students (Student_id, Student_name, Student_age, School_id, Class_id)
Teachers (Teacher_id, Teacher_name, Teacher_email, School_id)
Class_level (Class_id, Grade, Teacher_id)
Subjects (Subject_id, Subject_name, Teacher_id, Class_id)
Grades (Grade_id, Grade_value, Student_id, Class_id)
Events (Event_id, Event_name, Event_date, Event_location, School_id)
Facility (Facility_id, Facility_name, Facility_type, Facility_capacity, School_id)
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/cps-dashboard.git
cd cps-dashboard
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure the database connection:
   - Open `app.py`
   - Update the `DB_CONFIG` dictionary with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'CPS_Database'
}
```

5. Run the application:
```bash
python app.py
```

## Key Features Implementation

### Student Management
```python
@app.route('/students', methods=['GET', 'POST', 'DELETE'])
```
- Supports full CRUD operations
- Advanced filtering and search
- Grade tracking and performance metrics

### Event Management
```python
@app.route('/events')
```
- Comprehensive event filtering
- Status tracking (Today/Upcoming/Past)
- Search functionality
- Event statistics dashboard

### Analytics
```python
@app.route('/basic-analytics')
@app.route('/advanced-analytics')
```
- Two-tier analytics system
- Customizable analysis parameters
- Performance metrics and rankings
- Comparative statistics

## Security Considerations

- Database credentials should be stored in environment variables
- Input validation implemented for all form submissions
- SQL injection prevention through parameterized queries
- Error handling and logging implemented

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
