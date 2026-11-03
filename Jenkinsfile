pipeline {
    agent any
    environment {
        TARGET_URL = "http://127.0.0.1:3000/rest"
    }
    stages {
        stage('拉取GitHub测试代码') {
            steps {
                checkout scm
            }
        }
        stage('安装Python依赖包') {
            steps {
                sh '''
                    python3 -m pip install -r requirements.txt
                '''
            }
        }
        stage('执行pytest接口自动化测试') {
            steps {
                sh '''
                    python3 -m pytest testcases/ --alluredir=allure-results --clean-alluredir
                '''
            }
        }
    }
    post {
        always {
            allure includeProperties: false, results: [[path: 'allure-results']]
        }
    }
}
