pipeline {
    agent none
    stages {
        stage('Run tests') {
            parallel {
                stage('Functional tests') {
                    agent {
                        docker { image 'alpine:latest' }
                    }
                    steps {
                        withCredentials([file(credentialsId: 'project.properties', variable: 'projectproperties')]) {
                            sh 'git clone git@github.com:threatgrid/softserve-atqc.git'
                            sh 'cd ctrlibrary && python setup.py install'
                            sh 'pip3 install --upgrade --requirement code/requirements.txt'
                            sh 'cd code && flake8 .'
                            sh 'cd code && coverage run --source api/ -m pytest --verbose tests/unit/ && coverage report'
                            sh 'cp \$projectproperties project.properties'
                            sh 'cd code && pytest --verbose tests/functional/'
                        }
                    }
                stage('Unit tests') {
                    agent {
                        docker { image 'alpine:latest' }
                    }
                    steps {
                        withCredentials([file(credentialsId: 'project.properties', variable: 'projectproperties')]) {
                            sh 'pip3 install --upgrade --requirement code/requirements.txt'
                            sh 'cd code && flake8 .'
                            sh 'cd code && coverage run --source api/ -m pytest --verbose tests/unit/ && coverage report'
                        }
                    }
        stage('Test') {
            agent { docker
            { image 'ctrlib'
            args '-u 0:0'}}
            steps {
                withCredentials([file(credentialsId: 'project.properties', variable: 'projectproperties')]) {
                    sh 'pip3 install --upgrade --requirement code/requirements.txt'
                    sh 'cd code && flake8 .'
                    sh 'cd code && coverage run --source api/ -m pytest --verbose tests/unit/ && coverage report'
                    sh 'cp \$projectproperties project.properties'
                    sh 'cd code && pytest --verbose tests/functional/'
                }
            }
        }
        stage('Build') {
            steps {
                 sh 'docker build -t tr-05-urlscanio .'
                 sh 'docker run -d -p 9090:9090 --name tr-05-urlscanio tr-05-urlscanio'
                 sh 'while true; do if docker logs tr-05-urlscanio | grep "entered RUNNING state"; then break; else sleep 1; fi done'
                 sh 'curl -X POST -sSLi http://localhost:9090/health | grep "200 OK"'
                 sh 'curl -X GET -sSLi http://localhost:9090/watchdog | grep "200 OK"'
            }
        }
    }
}

