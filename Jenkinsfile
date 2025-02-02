pipeline {
    agent any

    environment {
        GITHUB_CREDENTIALS_ID = 'github-credential-id' // Replace with your Jenkins GitHub credentials ID
        REPO_URL = 'https://github.com/DrPlain/messaging_app.git' // Replace with your repository URL
        BRANCH = 'master' // Replace with the branch name you want to build
        VENV_DIR = '.venv' // Directory for Python virtual environment
        SECRET_KEY = 'django-insecure-u3aphu(8n9_#(us5r#yld$-#bdr5u=_c=t5-cx8p-x0by(rh$f'
        MYSQL_ROOT_PASSWORD='RHJQbGFpbi0wMDQ'
        MYSQL_DB='messaging_app'
        MYSQL_USER='DrPlain-messaging_app'
        MYSQL_PASSWORD='DrPlain-004'
        MYSQL_HOST='localhost'
        MYSQL_PORT=3306
        ALLOWED_HOSTS='localhost,127.0.0.1,192.168.49.2,0.0.0.0,myapp-service.default.svc.cluster.local,messaging-app.local'
        DB_ENGINE='django.db.backends.mysql'
        DOCKER_IMAGE_NAME = 'drplain004/messaging-app' // Replace with your Docker image name
        DOCKER_REGISTRY = 'docker.io' // Registry for docker hub
        DOCKER_CREDENTIALS_ID = 'docker-credentials-id' // Jenkins credentials for Docker registry
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo 'Checking out code from the Git branch...'
                    git branch: "${BRANCH}", credentialsId: "${GITHUB_CREDENTIALS_ID}", url: "${REPO_URL}", timeout: 300
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies from requirements.txt...'
                sh '''
                python3 -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip3 install --upgrade pip
                pip3 install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                . ${VENV_DIR}/bin/activate
                python manage.py test
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}"
                        dockerImage.push()
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed. Check logs for more details.'
        }
    }
    
}
