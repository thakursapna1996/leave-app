from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secure_secret_key_for_validation"  # needed for flash messages

# ------------------------------
# Setup basic logging
# ------------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Temporary in-memory data
requests_data = []


# ------------------------------
# Home Page
# ------------------------------
@app.route('/')
def home():
    return render_template('index.html', requests=requests_data)


# ------------------------------
# Add Leave Request
# ------------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_request():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        leave_type = request.form.get('leave_type', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()

        # --- Validation ---
        if not name or not leave_type or not start_date or not end_date or not reason:
            flash("❌ All fields are required!", "error")
            logging.warning("Form submission failed: Missing required fields.")
            return redirect(url_for('add_request'))

        # --- Validate date format ---
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            if e_date < s_date:
                flash("⚠️ End date cannot be before start date!", "error")
                logging.warning("Invalid date range entered.")
                return redirect(url_for('add_request'))
        except ValueError:
            flash("❌ Invalid date format! Use YYYY-MM-DD.", "error")
            return redirect(url_for('add_request'))

        # --- Save valid request ---
        new_request = {
            'name': name,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'status': 'Pending'
        }
        requests_data.append(new_request)
        logging.info(f"New leave request added for {name}.")
        flash("✅ Leave request submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('add.html')


# ------------------------------
# Edit Leave Request
# ------------------------------
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_request(index):
    if index >= len(requests_data):
        flash("Leave request not found!", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        leave_type = request.form.get('leave_type', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()

        if not all([name, leave_type, start_date, end_date, reason]):
            flash("❌ Please fill all fields before saving.", "error")
            return redirect(url_for('edit_request', index=index))

        requests_data[index].update({
            'name': name,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason
        })
        logging.info(f"Leave request for {name} updated.")
        flash("✅ Leave request updated successfully!", "success")
        return redirect(url_for('home'))

    req = requests_data[index]
    return render_template('edit.html', req=req, index=index)


# ------------------------------
# Delete Leave Request
# ------------------------------
@app.route('/delete/<int:index>')
def delete_request(index):
    if index < len(requests_data):
        deleted = requests_data.pop(index)
        logging.info(f"Leave request deleted: {deleted['name']}")
        flash("🗑️ Leave request deleted.", "info")
    else:
        flash("Leave request not found!", "error")
    return redirect(url_for('home'))


# ------------------------------
# Approve / Reject
# ------------------------------
@app.route('/approve/<int:index>')
def approve_request(index):
    if index < len(requests_data):
        requests_data[index]['status'] = 'Approved'
        logging.info(f"Leave approved for {requests_data[index]['name']}.")
    return redirect(url_for('home'))


@app.route('/reject/<int:index>')
def reject_request(index):
    if index < len(requests_data):
        requests_data[index]['status'] = 'Rejected'
        logging.info(f"Leave rejected for {requests_data[index]['name']}.")
    return redirect(url_for('home'))


# ------------------------------
# Run Flask App
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)