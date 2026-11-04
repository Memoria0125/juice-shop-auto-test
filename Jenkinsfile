pipeline {
    agent any

    options {
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        JUICE_SHOP_URL = "http://127.0.0.1:3000"
    }

    stages {
        stage('拉取GitHub测试代码') {
            steps {
                checkout scm
            }
        }

        stage('安装Python依赖包') {
            steps {
                bat '''
                    python -m pip install --disable-pip-version-check -r requirements.txt
                '''
            }
        }

        stage('执行pytest接口自动化测试') {
            steps {
                bat '''
                    python -m pytest testcases --alluredir=allure-results --clean-alluredir --junitxml=test-results/junit.xml
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results/junit.xml'
            allure includeProperties: false, results: [[path: 'allure-results']]
        }
    }
}
