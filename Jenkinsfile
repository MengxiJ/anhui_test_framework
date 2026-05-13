pipeline {
    agent any
    
    tools {
        python 'Python3.11'
        jdk 'JDK11'
    }
    
    environment {
        ALLURE_HOME = tool name: 'Allure', type: 'io.jenkins.plugins.allure.AllureToolInstallation'
        JMETER_HOME = tool name: 'JMeter', type: 'hudson.plugins.jmeter.JMeterInstallation'
    }
    
    stages {
        stage('代码检出') {
            steps {
                echo '开始检出代码...'
                checkout scm
                sh 'ls -la'
            }
        }
        
        stage('环境准备') {
            steps {
                echo '安装项目依赖...'
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install allure-pytest
                '''
            }
        }
        
        stage('代码质量检查') {
            parallel {
                stage('Flake8检查') {
                    steps {
                        echo '运行 Flake8 代码检查...'
                        sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true'
                    }
                }
                stage('Black格式检查') {
                    steps {
                        echo '运行 Black 格式检查...'
                        sh 'black --check . || true'
                    }
                }
            }
        }
        
        stage('运行API测试') {
            steps {
                echo '开始运行API自动化测试...'
                sh '''
                    pytest scripts/test_api_*.py -v \
                        --alluredir=output/allure/results \
                        --clean-alluredir \
                        -n auto
                '''
            }
            post {
                always {
                    echo 'API测试执行完成'
                }
            }
        }
        
        stage('运行UI测试') {
            steps {
                echo '开始运行UI自动化测试...'
                sh '''
                    pytest scripts/test_0*.py -v \
                        --alluredir=output/allure/results-ui \
                        --clean-alluredir
                '''
            }
            post {
                always {
                    echo 'UI测试执行完成'
                }
            }
        }
        
        stage('运行性能测试') {
            steps {
                echo '开始运行性能测试...'
                sh '''
                    mkdir -p output/performance
                    ${JMETER_HOME}/bin/jmeter -n \
                        -t performance/performance_test.jmx \
                        -l output/performance/result.jtl \
                        -e -o output/performance/report
                '''
            }
            post {
                always {
                    echo '性能测试执行完成'
                    archiveArtifacts artifacts: 'output/performance/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('生成测试报告') {
            steps {
                echo '生成Allure测试报告...'
                script {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'output/allure/results']]
                    ])
                }
            }
        }
    }
    
    post {
        always {
            echo '测试流程执行完成'
            archiveArtifacts artifacts: 'output/allure/results/**/*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'output/screenshot/**/*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'output/performance/**/*', allowEmptyArchive: true
        }
        
        success {
            echo '✅ 测试执行成功！'
            emailext(
                subject: '✅ 自动化测试执行成功 - ${PROJECT_NAME}',
                body: '''
                    <h2>测试执行成功</h2>
                    <p>项目: ${PROJECT_NAME}</p>
                    <p>构建号: ${BUILD_NUMBER}</p>
                    <p>构建地址: ${BUILD_URL}</p>
                    <p>测试报告: ${BUILD_URL}allure</p>
                    <p>性能测试报告: ${BUILD_URL}artifact/output/performance/report/index.html</p>
                ''',
                to: '${PROJECT_DEFAULT_RECIPIENTS}',
                mimeType: 'text/html'
            )
        }
        
        failure {
            echo '❌ 测试执行失败！'
            emailext(
                subject: '❌ 自动化测试执行失败 - ${PROJECT_NAME}',
                body: '''
                    <h2>测试执行失败</h2>
                    <p>项目: ${PROJECT_NAME}</p>
                    <p>构建号: ${BUILD_NUMBER}</p>
                    <p>构建地址: ${BUILD_URL}</p>
                    <p>请检查测试日志和报告</p>
                ''',
                to: '${PROJECT_DEFAULT_RECIPIENTS}',
                mimeType: 'text/html'
            )
        }
    }
}
