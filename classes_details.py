import streamlit as st
import mysql.connector
from mysql.connector import Error


# ======================
# MySQL Database Configuration
# ======================
def get_db_config():
    return {
        'host': 'localhost',
        'user': 'root',  # Change to your MySQL username
        'password': 'sa1382+',  # Change to your MySQL password
        'database': 'classes_db'
    }


# ======================
# Database Initialization
# ======================
def initialize_database():
    try:
        # First connect without specifying database
        config = get_db_config()
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )

        cursor = connection.cursor()

        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
        cursor.execute(f"USE {config['database']}")

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number VARCHAR(50),
                professor VARCHAR(100),
                time VARCHAR(50),
                title VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        return True

    except Error as e:
        st.error(f"Database initialization failed: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


# ======================
# Database Operations
# ======================
def save_class(number, professor, time, title):
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO classes (number, professor, time, title) VALUES (%s, %s, %s, %s)",
            (number, professor, time, title)
        )
        connection.commit()
        return True

    except Error as e:
        st.error(f"Failed to save class: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def get_classes():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, number, professor, time, title 
            FROM classes 
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

    except Error as e:
        st.error(f"Failed to fetch classes: {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def delete_class(class_id):
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM classes WHERE id = %s", (class_id,))
        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        st.error(f"Failed to delete class: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


# ======================
# Streamlit UI
# ======================
def main():
    st.title("📚 Class Manager")

    # Initialize database
    if not initialize_database():
        st.warning("Running in demo mode (data won't be saved)")
        demo_mode = True
    else:
        demo_mode = False

    # Define colors for boxes
    colors = ["#FFE4E1", "#E0FFFF", "#F0FFF0", "#FFF0F5"]
    border_colors = ["#FF69B4", "#20B2AA", "#9ACD32", "#FFA07A"]

    # Custom CSS
    st.markdown("""
        <style>
            .class-box {
                width: 100%;
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                border-left: 5px solid;
                font-size: 18px;
                line-height: 1.8;
                position: relative;
            }
            .delete-btn {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 14px;
                cursor: pointer;
                position: absolute;
                top: 10px;
                right: 10px;
            }
            .delete-btn:hover {
                background-color: #d32f2f;
            }
        </style>
    """, unsafe_allow_html=True)

    # Input Form
    form_data = {
        'number': '',
        'professor': '',
        'time': '',
        'title': ''
    }

    with st.form("class_form", clear_on_submit=True):
        st.subheader("➕ Add New Class")

        form_data['number'] = st.text_input("Class Number:", key="number_input")
        form_data['professor'] = st.text_input("Professor:", key="professor_input")
        form_data['time'] = st.text_input("Time:", key="time_input")
        form_data['title'] = st.text_input("Title:", key="title_input")

        submitted = st.form_submit_button("Save Class")

        if submitted:
            if all(form_data.values()):
                if not demo_mode:
                    if save_class(form_data['number'], form_data['professor'],
                                  form_data['time'], form_data['title']):
                        st.success("Class saved successfully!")
                        st.rerun()
                else:
                    st.success("Demo mode: Class would be saved here")
            else:
                st.warning("Please fill all fields!")

    # Display Classes
    st.subheader("📋 Saved Classes")

    if demo_mode:
        classes = []  # Empty list for demo mode
        st.info("Database not available - showing demo mode")
    else:
        classes = get_classes()

    if not classes:
        st.info("No classes found in database")
    else:
        for idx, class_info in enumerate(classes):
            color_idx = idx % len(colors)

            # Create columns for layout
            col1, col2 = st.columns([0.85, 0.15])

            with col1:
                st.markdown(
                    f"""
                    <div class="class-box" style="
                        background-color: {colors[color_idx]};
                        border-color: {border_colors[color_idx]};
                    ">
                        <strong>No:</strong> {class_info['number']}<br>
                        <strong>Professor:</strong> {class_info['professor']}<br>
                        <strong>Time:</strong> {class_info['time']}<br>
                        <strong>Title:</strong> {class_info['title']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("✕ Delete", key=f"delete_{class_info['id']}"):
                    if delete_class(class_info['id']):
                        st.success("Class deleted successfully!")
                        st.rerun()


if __name__ == "__main__":
    main()