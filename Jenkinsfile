pipeline {
    agent any

    environment {
        PYTHON_ENV = '/tmp/aceest-jenkins-venv'
        DOCKER_TEST_IMAGE = 'aceest-fitness:test'
        DOCKER_PROD_IMAGE = 'aceest-fitness:local'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checkout completed'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv $PYTHON_ENV
                    $PYTHON_ENV/bin/python -m pip install --upgrade pip
                    $PYTHON_ENV/bin/python -m pip install -r requirements.txt
                '''
            }
        }

stage('Run Pytest') {
    steps {
        sh '''
            $PYTHON_ENV/bin/python -m pytest \
                --cov=app \
                --cov=database \
                --cov-report=xml:coverage.xml \
                --cov-report=term-missing \
                -v
        '''
    }
}

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=aceest-fitness \
                            -Dsonar.projectName='ACEest Fitness' \
                            -Dsonar.sources=app.py,database.py,Dockerfile \
                            -Dsonar.tests=tests \
                            -Dsonar.test.inclusions=tests/**/*.py \
                            -Dsonar.exclusions=tests/**,.venv/**,**/__pycache__/**,.pytest_cache/**,original_versions/**,instance/**,coverage.xml \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Build Docker Test Image') {
            steps {
                sh '''
                    docker build --target test -t $DOCKER_TEST_IMAGE .
                '''
            }
        }

        stage('Run Docker Tests') {
            steps {
                sh '''
                    docker run --rm $DOCKER_TEST_IMAGE
                '''
            }
        }

        stage('Build Production Image') {
            steps {
                sh '''
                    docker build --target production -t $DOCKER_PROD_IMAGE .
                '''
            }
        }
    }

    post {
        success {
            echo 'ACEest Fitness CI Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins console output.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
