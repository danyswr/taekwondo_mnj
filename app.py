from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'RyujinYuna.000'  # Change this to your MySQL password
app.config['MYSQL_DB'] = 'taekwondo_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Add custom Jinja2 filters
@app.template_filter('to_datetime')
def to_datetime(date_str):
    """Convert a date string to a datetime object"""
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(str(date_str), '%Y-%m-%d')
    except (ValueError, TypeError):
        return datetime.now()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Athletes routes
@app.route('/athletes')
def athletes():
    cur = mysql.connection.cursor()
    
    # Get filter parameters
    gender_filter = request.args.get('gender', '')
    search_query = request.args.get('search', '')
    
    # Base query
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
        WHERE 1=1
    """
    
    # Apply filters
    if gender_filter:
        query += f" AND a.gender = '{gender_filter}'"
    
    if search_query:
        query += f" AND (a.full_name LIKE '%{search_query}%' OR d.name LIKE '%{search_query}%')"
    
    cur.execute(query)
    athletes = cur.fetchall()
    
    # Get dojangs and belt ranks for dropdowns
    cur.execute("SELECT * FROM dojangs")
    dojangs = cur.fetchall()
    
    cur.execute("SELECT * FROM belt_ranks")
    belt_ranks = cur.fetchall()
    
    cur.close()
    
    return render_template('athletes.html', 
                          athletes=athletes, 
                          dojangs=dojangs, 
                          belt_ranks=belt_ranks,
                          gender_filter=gender_filter,
                          search_query=search_query)

@app.route('/athletes/add', methods=['POST'])
def add_athlete():
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        weight = request.form['weight']
        height = request.form['height']
        gender = request.form['gender']
        belt_rank_id = request.form['belt_rank_id']
        dojang_id = request.form['dojang_id']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO athletes 
            (full_name, date_of_birth, weight, height, gender, belt_rank_id, dojang_id, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (full_name, date_of_birth, weight, height, gender, belt_rank_id, dojang_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Athlete added successfully!', 'success')
        return redirect(url_for('athletes'))

@app.route('/athletes/edit/<int:id>', methods=['GET', 'POST'])
def edit_athlete(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        weight = request.form['weight']
        height = request.form['height']
        gender = request.form['gender']
        belt_rank_id = request.form['belt_rank_id']
        dojang_id = request.form['dojang_id']
        
        cur.execute("""
            UPDATE athletes 
            SET full_name = %s, date_of_birth = %s, weight = %s, height = %s, 
                gender = %s, belt_rank_id = %s, dojang_id = %s, updated_at = NOW()
            WHERE id = %s
        """, (full_name, date_of_birth, weight, height, gender, belt_rank_id, dojang_id, id))
        
        mysql.connection.commit()
        flash('Athlete updated successfully!', 'success')
        return redirect(url_for('athletes'))
    
    # Get athlete data
    cur.execute("""
        SELECT * FROM athletes WHERE id = %s
    """, (id,))
    athlete = cur.fetchone()
    
    # Get dojangs and belt ranks for dropdowns
    cur.execute("SELECT * FROM dojangs")
    dojangs = cur.fetchall()
    
    cur.execute("SELECT * FROM belt_ranks")
    belt_ranks = cur.fetchall()
    
    cur.close()
    
    return render_template('edit_athlete.html', 
                          athlete=athlete, 
                          dojangs=dojangs, 
                          belt_ranks=belt_ranks)

@app.route('/athletes/delete/<int:id>', methods=['POST'])
def delete_athlete(id):
    cur = mysql.connection.cursor()
    
    # Check if athlete is in any matches
    cur.execute("""
        SELECT COUNT(*) as count FROM matches 
        WHERE blue_corner_id = %s OR red_corner_id = %s
    """, (id, id))
    result = cur.fetchone()
    
    if result['count'] > 0:
        flash('Cannot delete athlete who has participated in matches!', 'danger')
    else:
        cur.execute("DELETE FROM athletes WHERE id = %s", (id,))
        mysql.connection.commit()
        flash('Athlete deleted successfully!', 'success')
    
    cur.close()
    return redirect(url_for('athletes'))

# Matches routes
@app.route('/matches')
def matches():
    cur = mysql.connection.cursor()
    
    # Get filter parameters
    gender_filter = request.args.get('gender', '')
    search_query = request.args.get('search', '')
    title_filter = request.args.get('title', '')
    
    # Base query
    query = """
        SELECT m.*, 
               blue.full_name as blue_name, 
               red.full_name as red_name,
               blue.weight as blue_weight,
               red.weight as red_weight,
               blue.height as blue_height,
               red.height as red_height,
               blue.date_of_birth as blue_dob,
               red.date_of_birth as red_dob,
               blue_belt.name as blue_belt,
               red_belt.name as red_belt,
               blue_dojang.name as blue_dojang,
               red_dojang.name as red_dojang,
               t.name as title_name
        FROM matches m
        LEFT JOIN athletes blue ON m.blue_corner_id = blue.id
        LEFT JOIN athletes red ON m.red_corner_id = red.id
        LEFT JOIN belt_ranks blue_belt ON blue.belt_rank_id = blue_belt.id
        LEFT JOIN belt_ranks red_belt ON red.belt_rank_id = red_belt.id
        LEFT JOIN dojangs blue_dojang ON blue.dojang_id = blue_dojang.id
        LEFT JOIN dojangs red_dojang ON red.dojang_id = red_dojang.id
        LEFT JOIN match_titles t ON m.title_id = t.id
        WHERE 1=1
    """
    
    # Apply filters
    if gender_filter:
        query += f" AND m.gender = '{gender_filter}'"
    
    if search_query:
        query += f" AND (blue.full_name LIKE '%{search_query}%' OR red.full_name LIKE '%{search_query}%' OR t.name LIKE '%{search_query}%')"
    
    if title_filter:
        query += f" AND m.title_id = {title_filter}"
    
    # Order by most recent matches first
    query += " ORDER BY m.created_at DESC"
    
    cur.execute(query)
    matches = cur.fetchall()
    
    # Get all match titles for the dropdown
    cur.execute("SELECT * FROM match_titles ORDER BY name ASC")
    match_titles = cur.fetchall()
    
    # Add current date for age calculation in template
    now = datetime.now()
    
    # Calculate ages for athletes
    for match in matches:
        if match['blue_dob']:
            blue_dob = datetime.strptime(match['blue_dob'].strftime('%Y-%m-%d'), '%Y-%m-%d')
            blue_age = now.year - blue_dob.year - ((now.month, now.day) < (blue_dob.month, blue_dob.day))
            match['blue_age'] = blue_age
        
        if match['red_dob']:
            red_dob = datetime.strptime(match['red_dob'].strftime('%Y-%m-%d'), '%Y-%m-%d')
            red_age = now.year - red_dob.year - ((now.month, now.day) < (red_dob.month, red_dob.day))
            match['red_age'] = red_age
    
    cur.close()
    
    return render_template('matches.html', 
                          matches=matches,
                          gender_filter=gender_filter,
                          search_query=search_query,
                          title_filter=title_filter,
                          match_titles=match_titles,
                          now=now)

@app.route('/matches/create', methods=['GET'])
def create_match_form():
    cur = mysql.connection.cursor()
    
    # Get filter parameters for athletes
    gender_filter = request.args.get('gender', '')
    
    # Base query with all necessary data for filtering
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
        WHERE 1=1
    """
    
    # Apply gender filter
    if gender_filter:
        query += f" AND a.gender = '{gender_filter}'"
    
    # Order by name for easier selection
    query += " ORDER BY a.full_name ASC"
    
    cur.execute(query)
    athletes = cur.fetchall()
    
    # Add current date for age calculation in template
    now = datetime.now()
    
    cur.close()
    
    return render_template('create_match.html', 
                          athletes=athletes,
                          gender_filter=gender_filter,
                          now=now)

@app.route('/matches/add', methods=['POST'])
def add_match():
    if request.method == 'POST':
        title_id = request.form.get('title_id')
        title_name = request.form.get('title_name', '')
        blue_corner_id = request.form.get('blue_corner_id')
        red_corner_id = request.form.get('red_corner_id')
        gender = request.form.get('gender', '')
        
        if not blue_corner_id or not red_corner_id:
            flash('Both blue corner and red corner athletes are required!', 'danger')
            return redirect(url_for('matches'))
        
        cur = mysql.connection.cursor()
        
        # If a new title name is provided, create a new title
        if not title_id and title_name:
            cur.execute("""
                INSERT INTO match_titles 
                (name, created_at, updated_at) 
                VALUES (%s, NOW(), NOW())
            """, (title_name,))
            mysql.connection.commit()
            title_id = cur.lastrowid
        
        # If gender is not provided, get it from the blue corner athlete
        if not gender:
            cur.execute("SELECT gender FROM athletes WHERE id = %s", (blue_corner_id,))
            result = cur.fetchone()
            gender = result['gender'] if result else 'male'
        
        # Check if both athletes are of the same gender
        cur.execute("""
            SELECT a1.gender as blue_gender, a2.gender as red_gender
            FROM athletes a1, athletes a2
            WHERE a1.id = %s AND a2.id = %s
        """, (blue_corner_id, red_corner_id))
        
        result = cur.fetchone()
        
        if result and result['blue_gender'] != result['red_gender']:
            flash('Both athletes must be of the same gender!', 'danger')
            return redirect(url_for('matches'))
        
        try:
            # Insert match with title_id
            cur.execute("""
                INSERT INTO matches 
                (title_id, blue_corner_id, red_corner_id, gender, result, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, 'draw', NOW(), NOW())
            """, (title_id, blue_corner_id, red_corner_id, gender))
            
            mysql.connection.commit()
            match_id = cur.lastrowid
            
            flash('Match created successfully!', 'success')
            return redirect(url_for('matches'))
        except Exception as e:
            flash(f'Error creating match: {str(e)}', 'danger')
            return redirect(url_for('matches'))
        finally:
            cur.close()

@app.route('/matches/<int:id>')
def match_detail(id):
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT m.*, 
               blue.full_name as blue_name, 
               red.full_name as red_name,
               blue_belt.name as blue_belt,
               red_belt.name as red_belt,
               blue_dojang.name as blue_dojang,
               red_dojang.name as red_dojang,
               blue.weight as blue_weight,
               red.weight as red_weight,
               blue.height as blue_height,
               red.height as red_height,
               blue.date_of_birth as blue_dob,
               red.date_of_birth as red_dob
        FROM matches m
        LEFT JOIN athletes blue ON m.blue_corner_id = blue.id
        LEFT JOIN athletes red ON m.red_corner_id = red.id
        LEFT JOIN belt_ranks blue_belt ON blue.belt_rank_id = blue_belt.id
        LEFT JOIN belt_ranks red_belt ON red.belt_rank_id = red_belt.id
        LEFT JOIN dojangs blue_dojang ON blue.dojang_id = blue_dojang.id
        LEFT JOIN dojangs red_dojang ON red.dojang_id = red_dojang.id
        WHERE m.id = %s
    """, (id,))
    
    match = cur.fetchone()
    cur.close()
    
    if not match:
        flash('Match not found!', 'danger')
        return redirect(url_for('matches'))
    
    # Calculate ages
    now = datetime.now()
    
    if match['blue_dob']:
        blue_dob = datetime.strptime(match['blue_dob'].strftime('%Y-%m-%d'), '%Y-%m-%d')
        blue_age = now.year - blue_dob.year - ((now.month, now.day) < (blue_dob.month, blue_dob.day))
        match['blue_age'] = blue_age
    
    if match['red_dob']:
        red_dob = datetime.strptime(match['red_dob'].strftime('%Y-%m-%d'), '%Y-%m-%d')
        red_age = now.year - red_dob.year - ((now.month, now.day) < (red_dob.month, red_dob.day))
        match['red_age'] = red_age
    
    return render_template('match_detail.html', match=match)

@app.route('/matches/update_result/<int:id>', methods=['POST'])
def update_match_result(id):
    try:
        # Get the result from the form data
        result = request.form.get('result')
        
        # Validate result
        if result not in ['blue', 'red', 'draw']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Invalid result!'})
            flash('Invalid result!', 'danger')
            return redirect(url_for('match_detail', id=id))
        
        cur = mysql.connection.cursor()
        
        try:
            # Update the match result in the database
            cur.execute("""
                UPDATE matches 
                SET result = %s, updated_at = NOW()
                WHERE id = %s
            """, (result, id))
            
            mysql.connection.commit()
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Match result updated successfully!'})
            
            flash('Match result updated successfully!', 'success')
        except Exception as e:
            # Handle database errors
            mysql.connection.rollback()
            error_message = f'Error updating match result: {str(e)}'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': error_message})
            
            flash(error_message, 'danger')
        finally:
            cur.close()
        
        # Only redirect for non-AJAX requests
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect(url_for('match_detail', id=id))
        else:
            return jsonify({'success': True, 'message': 'Match result updated successfully!'})
    except Exception as e:
        # Handle any unexpected errors
        error_message = f'Unexpected error: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': error_message})
        
        flash(error_message, 'danger')
        return redirect(url_for('matches'))

@app.route('/matches/delete/<int:id>', methods=['POST'])
def delete_match(id):
    cur = mysql.connection.cursor()
    
    try:
        cur.execute("DELETE FROM matches WHERE id = %s", (id,))
        mysql.connection.commit()
        flash('Match deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting match: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('matches'))

# API endpoints for filtering athletes
@app.route('/api/athletes/filter', methods=['GET'])
def filter_athletes():
    # Get filter parameters
    gender = request.args.get('gender', '')
    search = request.args.get('search', '')
    age_min = request.args.get('age_min', '')
    age_max = request.args.get('age_max', '')
    weight_min = request.args.get('weight_min', '')
    weight_max = request.args.get('weight_max', '')
    height_min = request.args.get('height_min', '')
    height_max = request.args.get('height_max', '')
    
    cur = mysql.connection.cursor()
    
    # Base query
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
        WHERE 1=1
    """
    
    # Apply filters
    if gender:
        query += f" AND a.gender = '{gender}'"
    
    if search:
        query += f" AND (a.full_name LIKE '%{search}%' OR d.name LIKE '%{search}%')"
    
    # Age filter (calculate date range from age)
    if age_min or age_max:
        today = datetime.now()
        if age_max:
            min_date = today.replace(year=today.year - int(age_max) - 1)
            query += f" AND a.date_of_birth >= '{min_date.strftime('%Y-%m-%d')}'"
        if age_min:
            max_date = today.replace(year=today.year - int(age_min))
            query += f" AND a.date_of_birth <= '{max_date.strftime('%Y-%m-%d')}'"
    
    # Weight filter
    if weight_min:
        query += f" AND a.weight >= {weight_min}"
    if weight_max:
        query += f" AND a.weight <= {weight_max}"
    
    # Height filter
    if height_min:
        query += f" AND a.height >= {height_min}"
    if height_max:
        query += f" AND a.height <= {height_max}"
    
    # Order by name
    query += " ORDER BY a.full_name ASC"
    
    try:
        cur.execute(query)
        athletes = cur.fetchall()
        return jsonify(athletes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# API endpoint to get all athletes with details
@app.route('/api/athletes/all', methods=['GET'])
def get_all_athletes():
    cur = mysql.connection.cursor()
    
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
        ORDER BY a.full_name ASC
    """
    
    try:
        cur.execute(query)
        athletes = cur.fetchall()
        return jsonify(athletes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# API endpoint to get athlete by ID
@app.route('/api/athletes/<int:id>', methods=['GET'])
def get_athlete(id):
    cur = mysql.connection.cursor()
    
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
        WHERE a.id = %s
    """
    
    try:
        cur.execute(query, (id,))
        athlete = cur.fetchone()
        
        if not athlete:
            return jsonify({"error": "Athlete not found"}), 404
        
        return jsonify(athlete)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

@app.route('/api/stats')
def get_stats():
    cur = mysql.connection.cursor()
    
    # Get athlete count
    cur.execute("SELECT COUNT(*) as count FROM athletes")
    athlete_count = cur.fetchone()['count']
    
    # Get match count
    cur.execute("SELECT COUNT(*) as count FROM matches")
    match_count = cur.fetchone()['count']
    
    # Get male athlete count
    cur.execute("SELECT COUNT(*) as count FROM athletes WHERE gender = 'male'")
    male_count = cur.fetchone()['count']
    
    # Get female athlete count
    cur.execute("SELECT COUNT(*) as count FROM athletes WHERE gender = 'female'")
    female_count = cur.fetchone()['count']
    
    cur.close()
    
    return jsonify({
        'athlete_count': athlete_count,
        'match_count': match_count,
        'male_count': male_count,
        'female_count': female_count
    })

# Add these routes to handle match titles
@app.route('/api/match_titles', methods=['GET'])
def get_match_titles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM match_titles ORDER BY name ASC")
    titles = cur.fetchall()
    cur.close()
    return jsonify(titles)

@app.route('/api/match_titles/add', methods=['POST'])
def add_match_title():
    if request.method == 'POST':
        name = request.form['name']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO match_titles 
            (name, created_at, updated_at) 
            VALUES (%s, NOW(), NOW())
        """, (name,))
        
        mysql.connection.commit()
        title_id = cur.lastrowid
        cur.close()
        
        return jsonify({"success": True, "id": title_id, "name": name})

# Add this route to handle AJAX requests for match creation
@app.route('/matches/create_ajax', methods=['POST'])
def create_match_ajax():
    if request.method == 'POST':
        data = request.json
        title_id = data.get('title_id')
        title_name = data.get('title_name', '')
        blue_corner_id = data.get('blue_corner_id')
        red_corner_id = data.get('red_corner_id')
        gender = data.get('gender', '')
        
        cur = mysql.connection.cursor()
        
        # If a new title name is provided, create a new title
        if not title_id and title_name:
            cur.execute("""
                INSERT INTO match_titles 
                (name, created_at, updated_at) 
                VALUES (%s, NOW(), NOW())
            """, (title_name,))
            mysql.connection.commit()
            title_id = cur.lastrowid
        
        # If gender is not provided, get it from the blue corner athlete
        if not gender:
            cur.execute("SELECT gender FROM athletes WHERE id = %s", (blue_corner_id,))
            result = cur.fetchone()
            gender = result['gender'] if result else 'male'
        
        # Check if both athletes are of the same gender
        cur.execute("""
            SELECT a1.gender as blue_gender, a2.gender as red_gender
            FROM athletes a1, athletes a2
            WHERE a1.id = %s AND a2.id = %s
        """, (blue_corner_id, red_corner_id))
        
        result = cur.fetchone()
        
        if result and result['blue_gender'] != result['red_gender']:
            return jsonify({
                'success': False,
                'message': 'Both athletes must be of the same gender!'
            }), 400
        
        try:
            # Insert match with title_id
            cur.execute("""
                INSERT INTO matches 
                (title_id, blue_corner_id, red_corner_id, gender, result, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, 'draw', NOW(), NOW())
            """, (title_id, blue_corner_id, red_corner_id, gender))
            
            mysql.connection.commit()
            match_id = cur.lastrowid
            
            return jsonify({
                'success': True,
                'match_id': match_id,
                'message': 'Match created successfully!'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creating match: {str(e)}'
            }), 500
        finally:
            cur.close()
            

if __name__ == '__main__':
    app.run(debug=True)
