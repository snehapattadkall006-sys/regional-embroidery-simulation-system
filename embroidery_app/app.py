"""
Regional Embroidery Simulation System
Main Flask Application
"""

import re
import os
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'embroidery_secret_key_2024')

# -----------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',        # Change to your MySQL password
    'database': 'regional_embroidery'
}

def get_db():
    """Get a database connection."""
    return mysql.connector.connect(**DB_CONFIG)

# -----------------------------------------------
# DECORATORS
# -----------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# -----------------------------------------------
# VALIDATION HELPERS
# -----------------------------------------------
def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password: min 6 chars, upper, lower, digit."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    return True, ""

# -----------------------------------------------
# PUBLIC ROUTES
# -----------------------------------------------
@app.route('/')
def welcome():
    """Welcome / Landing page."""
    return render_template('welcome.html')

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

# -----------------------------------------------
# AUTH ROUTES
# -----------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([full_name, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('register.html')

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor()
            # Check duplicate email
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please login.', 'warning')
                return render_template('register.html')

            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, hashed)
            )
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('login.html')

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('welcome'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - email check."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('forgot_password.html')

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                session['reset_email'] = email
                flash('Email verified. Please reset your password.', 'success')
                return redirect(url_for('reset_password'))
            else:
                flash('Email not found in our system.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password page."""
    if 'reset_email' not in session:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        valid, msg = validate_password(new_password)
        if not valid:
            flash(msg, 'danger')
            return render_template('reset_password.html')

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor()
            hashed = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (hashed, session['reset_email'])
            )
            db.commit()
            session.pop('reset_email', None)
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Reset failed: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('reset_password.html')

# -----------------------------------------------
# USER DASHBOARD
# -----------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Get all designs for featured section
        cursor.execute("SELECT * FROM designs LIMIT 5")
        designs = cursor.fetchall()
        # Get user's favorites count
        cursor.execute("SELECT COUNT(*) as cnt FROM favorites WHERE user_id = %s", (session['user_id'],))
        fav_count = cursor.fetchone()['cnt']
        # Get saved designs count
        cursor.execute("SELECT COUNT(*) as cnt FROM saved_designs WHERE user_id = %s", (session['user_id'],))
        saved_count = cursor.fetchone()['cnt']
        # Featured embroidery of the month (first design)
        cursor.execute("SELECT * FROM designs ORDER BY id LIMIT 1")
        featured = cursor.fetchone()
    except Exception as e:
        designs, fav_count, saved_count, featured = [], 0, 0, None
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('dashboard.html',
        designs=designs, fav_count=fav_count,
        saved_count=saved_count, featured=featured,
        now_hour=datetime.now().hour)


@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Submit feedback."""
    user_name = request.form.get('user_name', '').strip()
    email = request.form.get('email', '').strip()
    rating = request.form.get('rating', '')
    message = request.form.get('message', '').strip()

    if not all([user_name, email, rating, message]):
        flash('All feedback fields are required.', 'danger')
        return redirect(url_for('dashboard'))

    if not validate_email(email):
        flash('Invalid email format.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError()
    except:
        flash('Invalid rating value.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO feedback (user_name, email, rating, message) VALUES (%s, %s, %s, %s)",
            (user_name, email, rating, message)
        )
        db.commit()
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        flash(f'Feedback submission failed: {str(e)}', 'danger')
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return redirect(url_for('dashboard'))

# -----------------------------------------------
# DESIGN ROUTES
# -----------------------------------------------
@app.route('/designs')
@login_required
def design_selection():
    """Design selection page with search/filter."""
    search = request.args.get('search', '')
    state_filter = request.args.get('state', '')
    fabric_filter = request.args.get('fabric', '')

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM designs WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE %s OR state LIKE %s)"
            params += [f'%{search}%', f'%{search}%']
        if state_filter:
            query += " AND state = %s"
            params.append(state_filter)
        if fabric_filter:
            query += " AND fabric_type LIKE %s"
            params.append(f'%{fabric_filter}%')

        cursor.execute(query, params)
        designs = cursor.fetchall()
        cursor.execute("SELECT DISTINCT state FROM designs")
        states = [row['state'] for row in cursor.fetchall()]
    except Exception as e:
        designs, states = [], []
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('design_selection.html',
        designs=designs, states=states,
        search=search, state_filter=state_filter)


@app.route('/design/<int:design_id>')
@login_required
def design_details(design_id):
    """Design details page."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM designs WHERE id = %s", (design_id,))
        design = cursor.fetchone()
        if not design:
            flash('Design not found.', 'warning')
            return redirect(url_for('design_selection'))

        # Track view
        cursor.execute("INSERT INTO design_views (design_name) VALUES (%s)", (design['name'],))
        db.commit()

        # Check if favorited
        cursor.execute("SELECT id FROM favorites WHERE user_id = %s AND design_id = %s",
                       (session['user_id'], design_id))
        is_favorited = cursor.fetchone() is not None
    except Exception as e:
        flash(f'Error loading design: {str(e)}', 'danger')
        return redirect(url_for('design_selection'))
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('design_details.html', design=design, is_favorited=is_favorited)


@app.route('/simulation/<int:design_id>')
@login_required
def simulation(design_id):
    """Simulation page."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM designs WHERE id = %s", (design_id,))
        design = cursor.fetchone()
        if not design:
            flash('Design not found.', 'warning')
            return redirect(url_for('design_selection'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('design_selection'))
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('simulation.html', design=design)


@app.route('/save-design', methods=['POST'])
@login_required
def save_design():
    """Save a simulation design."""
    design_id = request.form.get('design_id')
    if not design_id:
        return jsonify({'success': False, 'message': 'Design ID required'})

    try:
        db = get_db()
        cursor = db.cursor()
        # Avoid duplicates
        cursor.execute("SELECT id FROM saved_designs WHERE user_id = %s AND design_id = %s",
                       (session['user_id'], design_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Design already saved'})

        cursor.execute("INSERT INTO saved_designs (user_id, design_id) VALUES (%s, %s)",
                       (session['user_id'], design_id))
        db.commit()
        return jsonify({'success': True, 'message': 'Design saved successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

# -----------------------------------------------
# FAVORITES ROUTES
# -----------------------------------------------
@app.route('/favorites')
@login_required
def favorites():
    """View favorites page."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.*, f.id as fav_id
            FROM favorites f
            JOIN designs d ON f.design_id = d.id
            WHERE f.user_id = %s
        """, (session['user_id'],))
        favs = cursor.fetchall()
    except Exception as e:
        favs = []
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('favorites.html', favorites=favs)


@app.route('/toggle-favorite/<int:design_id>', methods=['POST'])
@login_required
def toggle_favorite(design_id):
    """Add or remove favorite."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM favorites WHERE user_id = %s AND design_id = %s",
                       (session['user_id'], design_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("DELETE FROM favorites WHERE user_id = %s AND design_id = %s",
                           (session['user_id'], design_id))
            db.commit()
            return jsonify({'success': True, 'action': 'removed', 'message': 'Removed from favorites'})
        else:
            cursor.execute("INSERT INTO favorites (user_id, design_id) VALUES (%s, %s)",
                           (session['user_id'], design_id))
            db.commit()
            return jsonify({'success': True, 'action': 'added', 'message': 'Added to favorites!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

# -----------------------------------------------
# SAVED DESIGNS
# -----------------------------------------------
@app.route('/saved-designs')
@login_required
def saved_designs():
    """View saved designs."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.*, sd.id as save_id, sd.saved_at
            FROM saved_designs sd
            JOIN designs d ON sd.design_id = d.id
            WHERE sd.user_id = %s
            ORDER BY sd.saved_at DESC
        """, (session['user_id'],))
        saves = cursor.fetchall()
    except Exception as e:
        saves = []
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('saved_designs.html', saved=saves)


@app.route('/remove-saved/<int:save_id>', methods=['POST'])
@login_required
def remove_saved(save_id):
    """Remove a saved design."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM saved_designs WHERE id = %s AND user_id = %s",
                       (save_id, session['user_id']))
        db.commit()
        flash('Design removed from saved.', 'info')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return redirect(url_for('saved_designs'))


@app.route('/track-download', methods=['POST'])
@login_required
def track_download():
    """Track simulation download."""
    design_name = request.form.get('design_name', '')
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO downloads (design_name) VALUES (%s)", (design_name,))
        db.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

# -----------------------------------------------
# LEARNING PAGE
# -----------------------------------------------
@app.route('/learning')
@login_required
def learning():
    """Learning / tutorial page."""
    return render_template('learning.html')

# -----------------------------------------------
# ADMIN ROUTES
# -----------------------------------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin = cursor.fetchone()

            if admin and check_password_hash(admin['password'], password):
                session['admin_id'] = admin['id']
                session['admin_email'] = admin['email']
                flash('Admin login successful.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with analytics."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Stats
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        total_users = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM designs")
        total_designs = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM saved_designs")
        total_saved = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM feedback")
        total_feedback = cursor.fetchone()['cnt']

        # Recent users
        cursor.execute("SELECT id, full_name, email, created_at FROM users ORDER BY created_at DESC LIMIT 10")
        recent_users = cursor.fetchall()

        # Recent feedback
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT 10")
        recent_feedback = cursor.fetchall()

        # Chart data: users by month
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as cnt
            FROM users GROUP BY month ORDER BY month DESC LIMIT 6
        """)
        users_by_month = cursor.fetchall()

        # Chart data: designs selected (by views)
        cursor.execute("""
            SELECT design_name, COUNT(*) as cnt
            FROM design_views GROUP BY design_name
        """)
        design_views_data = cursor.fetchall()

        # Chart data: saved by state
        cursor.execute("""
            SELECT d.state, COUNT(*) as cnt
            FROM saved_designs sd JOIN designs d ON sd.design_id = d.id
            GROUP BY d.state
        """)
        saved_by_state = cursor.fetchall()

        # Downloads
        cursor.execute("""
            SELECT design_name, COUNT(*) as cnt
            FROM downloads GROUP BY design_name
        """)
        downloads_data = cursor.fetchall()

        # All designs for admin table
        cursor.execute("SELECT * FROM designs ORDER BY state, name")
        all_designs = cursor.fetchall()

    except Exception as e:
        total_users = total_designs = total_saved = total_feedback = 0
        recent_users = recent_feedback = []
        users_by_month = design_views_data = saved_by_state = downloads_data = []
        all_designs = []
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()

    return render_template('admin_dashboard.html',
        total_users=total_users,
        total_designs=total_designs,
        total_saved=total_saved,
        total_feedback=total_feedback,
        recent_users=recent_users,
        recent_feedback=recent_feedback,
        users_by_month=users_by_month,
        design_views_data=design_views_data,
        saved_by_state=saved_by_state,
        downloads_data=downloads_data,
        all_designs=all_designs
    )


# -----------------------------------------------
# ADMIN SETUP ROUTE (Run once to create admin)
# -----------------------------------------------
@app.route('/admin/add-design', methods=['GET', 'POST'])
@admin_required
def admin_add_design():
    """Admin — add a new embroidery design."""
    if request.method == 'POST':
        state       = request.form.get('state', '').strip()
        name        = request.form.get('name', '').strip()
        image       = request.form.get('image', '').strip()
        description = request.form.get('description', '').strip()
        history     = request.form.get('history', '').strip()
        community   = request.form.get('community', '').strip()
        materials   = request.form.get('materials', '').strip()
        fabric_type = request.form.get('fabric_type', '').strip()
        cultural_significance = request.form.get('cultural_significance', '').strip()
        traditional_usage     = request.form.get('traditional_usage', '').strip()
        techniques            = request.form.get('techniques', '').strip()

        if not all([state, name, description]):
            flash('State, Name and Description are required.', 'danger')
            return render_template('admin_add_design.html')

        db = None; cursor = None
        try:
            db = get_db(); cursor = db.cursor()
            cursor.execute("""
                INSERT INTO designs
                (state, name, image, description, history, community, materials,
                 fabric_type, cultural_significance, traditional_usage, techniques)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (state, name, image, description, history, community, materials,
                  fabric_type, cultural_significance, traditional_usage, techniques))
            db.commit()
            flash(f'Design "{name}" added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if cursor: cursor.close()
            if db and db.is_connected(): db.close()

    return render_template('admin_add_design.html')


@app.route('/admin/delete-design/<int:design_id>', methods=['POST'])
@admin_required
def admin_delete_design(design_id):
    """Admin — delete a design."""
    db = None; cursor = None
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("DELETE FROM designs WHERE id = %s", (design_id,))
        db.commit()
        flash('Design deleted.', 'info')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/setup')
def admin_setup():
    """One-time admin account creation."""
    try:
        db = get_db()
        cursor = db.cursor()
        hashed = generate_password_hash('Admin@123')
        cursor.execute("DELETE FROM admin WHERE email = 'admin@embroidery.com'")
        cursor.execute(
            "INSERT INTO admin (email, password) VALUES (%s, %s)",
            ('admin@embroidery.com', hashed)
        )
        db.commit()
        return "Admin created! Email: admin@embroidery.com | Password: Admin@123"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if cursor: cursor.close()
        if db and db.is_connected(): db.close()


if __name__ == '__main__':
    app.run(debug=True)
