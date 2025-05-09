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
    
    # Base query
    query = """
        SELECT m.*, 
               blue.full_name as blue_name, 
               red.full_name as red_name
        FROM matches m
        LEFT JOIN athletes blue ON m.blue_corner_id = blue.id
        LEFT JOIN athletes red ON m.red_corner_id = red.id
        WHERE 1=1
    """
    
    # Apply filters
    if gender_filter:
        query += f" AND m.gender = '{gender_filter}'"
    
    if search_query:
        query += f" AND (blue.full_name LIKE '%{search_query}%' OR red.full_name LIKE '%{search_query}%' OR m.title LIKE '%{search_query}%')"
    
    cur.execute(query)
    matches = cur.fetchall()
    
    cur.close()
    
    return render_template('matches.html', 
                          matches=matches,
                          gender_filter=gender_filter,
                          search_query=search_query)

@app.route('/matches/create', methods=['GET'])
def create_match_form():
    cur = mysql.connection.cursor()
    
    # Get filter parameters for athletes
    gender_filter = request.args.get('gender', '')
    
    # Base query
    query = "SELECT * FROM athletes WHERE 1=1"
    
    # Apply gender filter
    if gender_filter:
        query += f" AND gender = '{gender_filter}'"
    
    cur.execute(query)
    athletes = cur.fetchall()
    
    cur.close()
    
    return render_template('create_match.html', 
                          athletes=athletes,
                          gender_filter=gender_filter)

@app.route('/matches/add', methods=['POST'])
def add_match():
    if request.method == 'POST':
        title = request.form['title']
        blue_corner_id = request.form['blue_corner_id']
        red_corner_id = request.form['red_corner_id']
        gender = request.form.get('gender', '')
        
        cur = mysql.connection.cursor()
        
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
        
        if result['blue_gender'] != result['red_gender']:
            flash('Both athletes must be of the same gender!', 'danger')
            return redirect(url_for('matches'))
        
        # Insert match
        cur.execute("""
            INSERT INTO matches 
            (title, blue_corner_id, red_corner_id, gender, result, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, 'draw', NOW(), NOW())
        """, (title, blue_corner_id, red_corner_id, gender))
        
        mysql.connection.commit()
        match_id = cur.lastrowid
        cur.close()
        
        flash('Match created successfully!', 'success')
        return redirect(url_for('matches'))

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
               red.height as red_height
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
    
    return render_template('match_detail.html', match=match)

@app.route('/matches/update_result/<int:id>', methods=['POST'])
def update_match_result(id):
    result = request.form['result']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE matches 
        SET result = %s, updated_at = NOW()
        WHERE id = %s
    """, (result, id))
    
    mysql.connection.commit()
    cur.close()
    
    flash('Match result updated!', 'success')
    return redirect(url_for('match_detail', id=id))

@app.route('/matches/delete/<int:id>', methods=['POST'])
def delete_match(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM matches WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Match deleted successfully!', 'success')
    return redirect(url_for('matches'))

# API endpoints for filtering athletes
@app.route('/api/athletes/filter', methods=['GET'])
def filter_athletes():
    gender = request.args.get('gender', '')
    
    cur = mysql.connection.cursor()
    
    query = """
        SELECT id, full_name, gender
        FROM athletes
        WHERE 1=1
    """
    
    if gender:
        query += f" AND gender = '{gender}'"
    
    cur.execute(query)
    athletes = cur.fetchall()
    cur.close()
    
    return jsonify(athletes)

# New API endpoint to get all athletes with details
@app.route('/api/athletes/all', methods=['GET'])
def get_all_athletes():
    cur = mysql.connection.cursor()
    
    query = """
        SELECT a.*, d.name as dojang_name, b.name as belt_rank
        FROM athletes a
        LEFT JOIN dojangs d ON a.dojang_id = d.id
        LEFT JOIN belt_ranks b ON a.belt_rank_id = b.id
    """
    
    cur.execute(query)
    athletes = cur.fetchall()
    cur.close()
    
    return jsonify(athletes)

# Add this route to app.py
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

if __name__ == '__main__':
    app.run(debug=True)