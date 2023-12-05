from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
api = Api(app)


# Function to create a connection to the MySQL database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='toor',
            database='xyz'
        )
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

    return None


# Function to close the database connection
def close_connection(connection):
    try:
        if connection:
            connection.close()
    except Error as e:
        print(f"Error closing connection: {e}")


# Function to convert date objects to string format
def convert_dates_to_string(employee):
    if employee:
        employee['dob'] = employee['dob'].strftime('%Y-%m-%d')
        employee['date_of_joining'] = employee['date_of_joining'].strftime('%Y-%m-%d')
        employee['created_at'] = employee['created_at'].strftime('%Y-%m-%d %H:%M:%S') if employee[
            'created_at'] else None
        employee['last_edit_at'] = employee['last_edit_at'].strftime('%Y-%m-%d %H:%M:%S') if employee[
            'last_edit_at'] else None
    return employee


# Resource for individual employee operations (GET, PUT, DELETE)
class EmployeeResource(Resource):
    def get(self, employee_id):
        try:
            connection = create_connection()

            if connection:
                cursor = connection.cursor(dictionary=True)  # Use dictionary=True to fetch rows as dictionaries
                sql = "SELECT * FROM employees WHERE id = %s"
                cursor.execute(sql, (employee_id,))
                employee = cursor.fetchone()
                close_connection(connection)

                employee = convert_dates_to_string(employee)

                if employee:
                    return {"result": employee}, 200
                else:
                    return jsonify(message='Employee not found'), 404

        except Error as e:
            print(f"Error in GET request: {e}")
            return jsonify(error='Internal Server Error', details=str(e)), 500

    def put(self, employee_id):
        try:
            data = request.get_json()

            connection = create_connection()

            if connection:
                cursor = connection.cursor()

                sql = """UPDATE employees
                         SET name=%s, dob=%s, designation=%s, company=%s, 
                             date_of_joining=%s, contact=%s, email=%s, last_edit_at=%s
                         WHERE id=%s"""

                cursor.execute(sql, (
                    data.get('name'),
                    data.get('dob'),
                    data.get('designation'),
                    data.get('company'),
                    data.get('date_of_joining'),
                    data.get('contact'),
                    data.get('email'),
                    datetime.utcnow(),
                    employee_id
                ))

                connection.commit()
                close_connection(connection)

                return jsonify(message='Employee updated successfully'), 200

        except Error as e:
            print(f"Error in PUT request: {e}")
            return jsonify(error='Internal Server Error', details=str(e)), 500

    def delete(self, employee_id):
        try:
            connection = create_connection()

            if connection:
                cursor = connection.cursor()

                sql = "DELETE FROM employees WHERE id=%s"
                cursor.execute(sql, (employee_id,))

                connection.commit()
                close_connection(connection)

                return jsonify(message='Employee deleted successfully'), 200

        except Error as e:
            print(f"Error in DELETE request: {e}")
            return jsonify(error='Internal Server Error', details=str(e)), 500


# Resource for handling a list of employees (GET all, POST to add)
class EmployeesResource(Resource):
    def get(self):
        try:
            connection = create_connection()

            if connection:
                cursor = connection.cursor(dictionary=True)  # Use dictionary=True to fetch rows as dictionaries
                sql = "SELECT * FROM employees"
                cursor.execute(sql)
                employees = cursor.fetchall()
                close_connection(connection)

                employees = [convert_dates_to_string(employee) for employee in employees]
                print(employees)
                return {"result": employees}, 200

        except Error as e:
            print(f"Error in GET request: {e}")
            return jsonify(error='Internal Server Error', details=str(e)), 500

    def post(self):
        try:
            data = request.get_json()

            connection = create_connection()

            if connection:
                cursor = connection.cursor()

                sql = """INSERT INTO employees 
                         (name, dob, designation, company, date_of_joining, contact, email, created_at) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

                cursor.execute(sql, (
                    data['name'],
                    data['dob'],
                    data['designation'],
                    data['company'],
                    data['date_of_joining'],
                    data['contact'],
                    data['email'],
                    datetime.utcnow()
                ))

                connection.commit()
                close_connection(connection)

                return jsonify(message='Employee added successfully'), 201

        except Error as e:
            print(f"Error in POST request: {e}")
            return jsonify(error='Internal Server Error', details=str(e)), 500


# Define the routes for the resources
api.add_resource(EmployeeResource, '/employee/<int:employee_id>')
api.add_resource(EmployeesResource, '/employees')

if __name__ == '__main__':
    app.run(debug=True)
