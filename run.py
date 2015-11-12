"""
Run this to start the Hetaira app.
"""

from hetaira import app

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])

