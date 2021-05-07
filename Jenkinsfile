pipeline {
    agent {
        label 'jenkins'
    }
    environment {
        app_name = "tr-05-urlscanio"
    }
    stages {
        stage('Build') {
            when {
                anyOf {
                    branch 'master'; branch 'develop'
                    changeRequest target: 'master' ; changeRequest target: 'develop'
                }
            }
            stages {
                stage('Run container and health-check') {
                    steps {
                        sh 'docker build -t ${app_name}:${BUILD_NUMBER} .'
                        sh 'docker run -d -p 9090:9090 --name ${app_name} ${app_name}:${BUILD_NUMBER}'
                        sh 'while true; do if docker logs ${app_name} | grep "entered RUNNING state"; then break; else sleep 1; fi done'
                        sh 'curl -X POST -sSLi http://localhost:9090/health | grep "200 OK"'
                        sh 'curl -X GET -sSLi http://localhost:9090/watchdog | grep "200 OK"'
                    }
                }
            }
        }
       stage('Test') {
           parallel {
               stage('Functional tests - Stage 1') {
                   agent {
                       docker {
                           image 'python:latest'
                           args '-u 0'
                           reuseNode true
                       }
                   }
                   steps {
                       withCredentials([string(credentialsId: 'access_token', variable: 'TOKEN')]) {
                           withCredentials([file(credentialsId: 'project.properties', variable: 'projectproperties')]) {
                               sh 'git clone "https://$TOKEN@github.com/CiscoSecurity/softserve-atqc.git"'
                               sh "sed -i 's|tests/functional|code/tests/functional|g' ./softserve-atqc/ctrlibrary/core/config.py"
                               sh 'cd ./softserve-atqc && python setup.py install'
                               sh 'cd ./code pwd && pip install --upgrade --requirement requirements.txt'
                               sh 'flake8 .'
                               sh 'cp \$projectproperties ./code/tests/functional/project.properties'
                               sh 'pytest --verbose ./code/tests/functional'
                           }
                       }
                   }
               }
               stage('Unit tests') {
                   agent {
                       docker {
                           image 'python:latest'
                           args '-u 0'
                           reuseNode true
                       }
                   }
                   steps {
                       sh 'cd ./code && pip install --upgrade --requirement requirements.txt'
                       sh 'flake8 .'
                       sh 'cd ./code && coverage run --source ./api -m pytest --verbose ./tests/unit && coverage report'
                   }
               }
               stage('Functional tests - Stage 2') {
                   agent {
                       docker {
                           image 'postman/newman:latest'
                           args '-u 0 --network=host --entrypoint=""'
                       }
                   }
                   steps {
                       withCredentials([file(credentialsId: 'urlscanio_collection', variable: 'urlscanio_collection')]) {
                           sh 'cp \$urlscanio_collection /urlscanio.postman_collection.json'
                           sh 'newman run /urlscanio.postman_collection.json'
                       }
                   }
               }
           }
       }
        stage('Push container to registry') {
            when {
                anyOf {
                    branch 'master'
                    changeRequest target: 'master'
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_credentials', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    script {
                        def props = readJSON file: 'code/container_settings.json'
                        app_ver = props['VERSION']
                        docker.withRegistry('https://registry.hub.docker.com', 'dockerhub_credentials') {
                            def app = docker.build('ciscosecurity/${app_name}:${app_ver}')
                            app.push()
                            app.push("latest")
                        }
                    }
                }
            }
        }
    }
    post {
        cleanup {
            sh 'docker rm -f ${app_name}'
            cleanWs()
        }
    }
}
