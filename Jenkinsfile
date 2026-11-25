pipeline {
    agent any
    stages {
        stage('Set up Python') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install --upgrade pip'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }
        stage('Run tests') {
            steps {
                sh '.venv/bin/python -m pytest -n 2'
            }
        }
    }
    post {
        always {
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'pytest-report.html',
                reportName: 'Pytest HTML Report',
                allowMissing: true,
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
            archiveArtifacts artifacts: 'reports/**, screenshots/**, logs/**',
                             allowEmptyArchive: true
        }
    }
}
