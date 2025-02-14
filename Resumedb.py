import sqlite3
import os
from datetime import datetime

class ResumeDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()

    def initialize_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create tables
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT,
                state TEXT,
                phone TEXT,
                email TEXT
            );

            CREATE TABLE IF NOT EXISTS work_experience (
                id INTEGER PRIMARY KEY,
                company TEXT,
                location TEXT,
                position TEXT,
                start_date TEXT,
                end_date TEXT,
                current_job BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS job_responsibilities (
                id INTEGER PRIMARY KEY,
                work_experience_id INTEGER,
                responsibility TEXT,
                FOREIGN KEY (work_experience_id) REFERENCES work_experience(id)
            );
            
            CREATE TABLE IF NOT EXISTS technical_skills (
                id INTEGER PRIMARY KEY,
                category TEXT,
                skill_name TEXT
            );
            
            CREATE TABLE IF NOT EXISTS software_skills (
                id INTEGER PRIMARY KEY,
                software_name TEXT
            );

            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY,
                institution TEXT,
                degree TEXT,
                major TEXT,
                minor TEXT,
                status TEXT
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                status TEXT
            );

            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                category TEXT,
                skill TEXT
            );

            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY,
                name TEXT,
                institution TEXT
            );
        ''')
        # Insert Technical Skills
        technical_skills = [
            ('Database Management', 'Database Management'),
            ('Document Control', 'Document Control Systems'),
            ('Metadata', 'Metadata Standards'),
            ('OCR', 'OCR Technologies'),
            ('Quality Assurance', 'Quality Assurance Protocols'),
            ('Records Management', 'Records Management Systems'),
            ('Workflow', 'Workflow Optimization')
        ]
        
        for skill in technical_skills:
            self.cursor.execute('''
                INSERT OR IGNORE INTO technical_skills (category, skill_name)
                VALUES (?, ?)
            ''', skill)

        # Insert Software Skills
        software_skills = [
            'Document Management Systems',
            'Microsoft Access',
            'Microsoft Excel',
            'Pressero',
            'Python',
            'SQL'
        ]
        
        for skill in software_skills:
            self.cursor.execute('''
                INSERT OR IGNORE INTO software_skills (software_name)
                VALUES (?)
            ''', (skill,))

        # Insert job responsibilities after ensuring work experiences exist
        # First, insert all work experiences
        work_experiences = [
            ('Crisp Imaging', 'Costa Mesa, Ca', 'Data Analyst & Records Management Specialist', '2023-09', '2024-08', False),
            ('ANJ', 'Corona, CA', 'Founder & Records Management Consultant', '2024-01', None, True),
            ('Fleetwood Windows & Doors', 'Corona, Ca', 'Saw Operator', '2018-05', '2023-05', False),
            ("Ferny's Tacos", 'Corona, CA', 'Operations & Events Coordinator', '2014-01', None, True),
            ('Fender', 'Corona, CA', 'Guitar Assembly Technician', '2017-01', '2017-05', False),
            ('Silvercrest', 'Corona, CA', 'Roofer/Framing', '2016-01', '2016-10', False)
        ]
        
        for exp in work_experiences:
            self.cursor.execute('''
                INSERT OR IGNORE INTO work_experience (company, location, position, start_date, end_date, current_job)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', exp)
        
        self.conn.commit()

        # Now insert responsibilities
        job_responsibilities = {
            'Crisp Imaging': [
                'Led and managed scanning technician team, implementing standardized workflows',
                'Oversaw end-to-end document management process',
                'Developed and implemented Python automation scripts',
                'Developed dual QR code scanning automation',
                'Initiated development of a QR code labeling system',
                'Implemented comprehensive quality assurance procedures',
                'Designed and built client storefronts using Pressero'
            ],
            "Ferny's Tacos": [
                'Developed and maintain comprehensive digital system for event management',
                'Implemented inventory tracking and vendor management systems',
                'Created documentation framework for event planning'
            ],
            'Fender': [
                'Maintained comprehensive production documentation',
                'Operated tracking systems for daily metrics'
            ]
        }

        for company, responsibilities in job_responsibilities.items():
            self.cursor.execute('SELECT id FROM work_experience WHERE company = ?', (company,))
            result = self.cursor.fetchone()
            
            if result:
                work_exp_id = result[0]
                for resp in responsibilities:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO job_responsibilities (work_experience_id, responsibility)
                        VALUES (?, ?)
                    ''', (work_exp_id, resp))
            else:
                print(f"Warning: Company '{company}' not found in work_experience table")

        self.conn.commit()

    def insert_initial_data(self):
        """Insert initial resume data"""
        # Personal Info
        self.cursor.execute('''
            INSERT OR IGNORE INTO personal_info (name, city, state, phone, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Aldo Garcia', 'Corona', 'CA', '(951) 410-5368', 'Aldogarciaa988@gmail.com'))

        # Work Experience
        work_experiences = [
            ('Crisp Imaging', 'Costa Mesa, Ca', 'Data Analyst & Records Management Specialist', '2023-09', '2024-08', False),
            ('ANJ', 'Corona, CA', 'Founder & Records Management Consultant', '2024-01', None, True),
            ('Fleetwood Windows & Doors', 'Corona, Ca', 'Saw Operator', '2018-05', '2023-05', False),
            ("Ferny's Tacos", 'Corona, CA', 'Operations & Events Coordinator', '2014-01', None, True),
            ('Fender', 'Corona, CA', 'Guitar Assembly Technician', '2017-01', '2017-05', False),
            ('Silvercrest', 'Corona, CA', 'Roofer/Framing', '2016-01', '2016-10', False)
        ]
        
        for exp in work_experiences:
            self.cursor.execute('''
                INSERT OR IGNORE INTO work_experience (company, location, position, start_date, end_date, current_job)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', exp)

        # Education
        self.cursor.execute('''
            INSERT OR IGNORE INTO education (institution, degree, major, minor, status)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Riverside Community College', "Associate's Degree", 'Public Administration', 'Computer Science', 'In Progress'))

        # Projects
        projects = [
            ('Box Tracker ID System', 'Python-based tracking solution utilizing QR codes integrated with Google Sheets API', 'In Development'),
            ('Dual QR Code Merger', 'Tool to handle projects involving both small and large format documents', 'Completed'),
            ('File Compression and Optimization', 'Python program to compress images without quality loss', 'Completed'),
            ('Text Document Rotation System', 'Intelligent document orientation correction system', 'In Development')
        ]
        
        for project in projects:
            self.cursor.execute('''
                INSERT OR IGNORE INTO projects (name, description, status)
                VALUES (?, ?, ?)
            ''', project)

        self.conn.commit()

    def add_work_experience(self):
        """Add new work experience"""
        company = input("Enter company name: ")
        location = input("Enter location: ")
        position = input("Enter position: ")
        start_date = input("Enter start date (YYYY-MM): ")
        current_job = input("Is this your current job? (y/n): ").lower() == 'y'
        end_date = None if current_job else input("Enter end date (YYYY-MM): ")

        self.cursor.execute('''
            INSERT INTO work_experience (company, location, position, start_date, end_date, current_job)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (company, location, position, start_date, end_date, current_job))
        self.conn.commit()

    def view_technical_skills(self):
        """View all technical skills"""
        self.cursor.execute('SELECT category, skill_name FROM technical_skills')
        skills = self.cursor.fetchall()
        
        print("\n=== Technical Skills ===")
        for skill in skills:
            print(f"{skill[0]}: {skill[1]}")

    def view_software_skills(self):
        """View all software skills"""
        self.cursor.execute('SELECT software_name FROM software_skills')
        skills = self.cursor.fetchall()
        
        print("\n=== Software Skills ===")
        for skill in skills:
            print(skill[0])

    def view_responsibilities(self, company=None):
        """View job responsibilities for a specific company or all companies"""
        if company:
            self.cursor.execute('''
                SELECT w.company, r.responsibility 
                FROM job_responsibilities r
                JOIN work_experience w ON r.work_experience_id = w.id
                WHERE w.company LIKE ?
                ORDER BY w.company
            ''', (f'%{company}%',))
        else:
            self.cursor.execute('''
                SELECT w.company, r.responsibility 
                FROM job_responsibilities r
                JOIN work_experience w ON r.work_experience_id = w.id
                ORDER BY w.company
            ''')
            
        responsibilities = self.cursor.fetchall()
        
        if responsibilities:
            print("\n=== Job Responsibilities ===")
            current_company = None
            for resp in responsibilities:
                if resp[0] != current_company:
                    current_company = resp[0]
                    print(f"\n{current_company}:")
                print(f"• {resp[1]}")
        else:
            print("No responsibilities found.")

    def view_all_experience(self):
        """View all work experience"""
        self.cursor.execute('''
            SELECT company, position, start_date, end_date, current_job
            FROM work_experience
            ORDER BY start_date DESC
        ''')
        experiences = self.cursor.fetchall()
        
        print("\n=== Work Experience ===")
        for exp in experiences:
            end_date = "Present" if exp[4] else exp[3]
            print(f"\nCompany: {exp[0]}")
            print(f"Position: {exp[1]}")
            print(f"Period: {exp[2]} - {end_date}")

    def view_all_projects(self):
        """View all projects"""
        self.cursor.execute('''
            SELECT name, description, status
            FROM projects
            ORDER BY status DESC
        ''')
        projects = self.cursor.fetchall()
        
        print("\n=== Projects ===")
        for proj in projects:
            print(f"\nName: {proj[0]}")
            print(f"Description: {proj[1]}")
            print(f"Status: {proj[2]}")

    def add_project(self):
        """Add new project"""
        name = input("Enter project name: ")
        description = input("Enter project description: ")
        status = input("Enter project status (Completed/In Development): ")

        self.cursor.execute('''
            INSERT INTO projects (name, description, status)
            VALUES (?, ?, ?)
        ''', (name, description, status))
        self.conn.commit()

    def search_experience(self):
        """Search work experience by company or position"""
        search_term = input("Enter company name or position to search: ")
        self.cursor.execute('''
            SELECT company, position, start_date, end_date
            FROM work_experience
            WHERE company LIKE ? OR position LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        results = self.cursor.fetchall()
        if results:
            print("\nSearch results:")
            for result in results:
                print(f"\nCompany: {result[0]}")
                print(f"Position: {result[1]}")
                print(f"Period: {result[2]} - {result[3] or 'Present'}")
        else:
            print("No matching results found.")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    db_path = r"C:\Users\aldog\OneDrive\Desktop\Expenses data base\resume.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db = ResumeDatabase(db_path)
    db.insert_initial_data()

    while True:
        print("\n=== Resume Database Manager ===")
        print("1. Add new work experience")
        print("2. View all work experience")
        print("3. Add new project")
        print("4. View all projects")
        print("5. Search work experience")
        print("6. View technical skills")
        print("7. View software skills")
        print("8. View job responsibilities")
        print("9. Exit")

        choice = input("\nEnter your choice (1-9): ")

        if choice == '1':
            db.add_work_experience()
        elif choice == '2':
            db.view_all_experience()
        elif choice == '3':
            db.add_project()
        elif choice == '4':
            db.view_all_projects()
        elif choice == '5':
            db.search_experience()
        elif choice == '6':
            db.view_technical_skills()
        elif choice == '7':
            db.view_software_skills()
        elif choice == '8':
            company = input("Enter company name to filter (or press Enter for all): ")
            db.view_responsibilities(company if company else None)
        elif choice == '9':
            db.close()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()