# lib/review.py

from lib import CONN, CURSOR  # Assuming these are defined in lib/__init__.py

class Review:
    all_reviews = {}  # Dictionary to cache Review instances

    def __init__(self, year, summary, employee_id=None):
        self.id = None  # This will be set when saved to the database
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"Review(id={self.id}, year={self.year}, summary='{self.summary}', employee_id={self.employee_id})"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            summary TEXT NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        CURSOR.execute("""
        INSERT INTO reviews (year, summary, employee_id)
        VALUES (?, ?, ?)
        """, (self.year, self.summary, self.employee_id))
        
        self.id = CURSOR.lastrowid  # Set the id to the primary key of the new row
        Review.all_reviews[self.id] = self  # Cache the instance
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id, year, summary, employee_id = row
        if review_id in cls.all_reviews:
            return cls.all_reviews[review_id]
        
        review = cls(year, summary, employee_id)
        review.id = review_id
        cls.all_reviews[review_id] = review
        return review

    @classmethod
    def find_by_id(cls, review_id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self, year=None, summary=None, employee_id=None):
        if year is not None:
            self.year = year
        if summary is not None:
            self.summary = summary
        if employee_id is not None:
            self.employee_id = employee_id

        CURSOR.execute("""
        UPDATE reviews
        SET year = ?, summary = ?, employee_id = ?
        WHERE id = ?
        """, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        del Review.all_reviews[self.id]
        self.id = None  # Clear the id to indicate it's no longer in the database
        CONN.commit()

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property methods for validation
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise Exception("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise Exception("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise Exception("Employee ID must be an integer.")
        self._employee_id = value

# Update Employee class
# Assuming the Employee class is in the same module or can be imported
class Employee:
    # Other methods...
    
    def reviews(self):
        from lib.review import Review  # Importing here to avoid circular imports
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]
