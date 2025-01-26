pipeline {
    agent any

    environment {
        GITHUB_CREDENTIALS_ID = 'github-credential-id' // Replace with your Jenkins GitHub credentials ID
        REPO_URL = 'https://github.com/DrPlain/messaging_app.git' // Replace with your repository URL
        BRANCH = 'master' // Replace with the branch name you want to build
        VENV_DIR = '.venv' // Directory for Python virtual environment
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo 'Checking out code from the Git branch...'
                    git branch: "${BRANCH}", credentialsId: "${GITHUB_CREDENTIALS_ID}", url: "${REPO_URL}", timeout: 20
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies from requirements.txt...'
                sh '''
                python3 -m venv ${VENV_DIR}
                source ${VENV_DIR}/bin/activate
                pip3 install --upgrade pip
                pip3 install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests using pytest...'
                sh '''
                source ${VENV_DIR}/bin/activate
                pytest messaging_app --junitxml=report.xml
                '''
            }
        }

        stage('Generate Report') {
            steps {
                echo 'Archiving test results...'
                junit 'report.xml' // Archive the test report in JUnit format
            }
        }
    }

    post {
        always {
            node {
                echo 'Cleaning up workspace...'
                cleanWs()
            }
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed. Check logs for more details.'
        }
    }

}
