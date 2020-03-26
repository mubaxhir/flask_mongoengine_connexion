# Import of the required libraries

import connexion

# Requirement for Windows only

import sys
sys.path.append('C:/Dev/Python/withchartsapi_v0.2.5/api/')


# Definition of the app using Connexion

def main():
    app = connexion.FlaskApp(__name__, specification_dir='openapi/')
    app.add_api('openapi.yaml')
    app.run(port=8080,debug=True)

if __name__ == '__main__':
    main()
