pipeline {
  agent { label 'node1' }

  stages {
    stage('Start Notification') {
      steps {
        script {
          def message = "This prod_infra pipeline has been triggerd"
          def jsonPayload = "{\"text\": \"${message}\"}"
          sh """
            curl -X POST \\
            -H "Content-Type: application/json" \\
            -d '${jsonPayload}' \\
            "https://chat.googleapis.com/v1/spaces/AAQAoL3O840/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=iqBfBelvIk5ZaQ55RhdOTR0s-IwkOVm_ZCsD23SWsbk"
          """
        }
      }
    }

    stage('filesystem scan') {
      steps {
        script {
          def reportFile = 'trivy-filescan-report.json'
          def webhookUrl = 'https://chat.googleapis.com/v1/spaces/AAQAoL3O840/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=iqBfBelvIk5ZaQ55RhdOTR0s-IwkOVm_ZCsD23SWsbk'
          def exitcode = sh(
            script: """
              trivy fs --scanners vuln,secret,misconfig --exit-code 1 --format json -o ${reportFile} .
              """,
            returnStatus: true
          )
          archiveArtifacts artifacts: "${reportFile}", fingerprint: true

          if (exitcode !=0) {
            echo "Vulnerabilities found in file scan!"
            def message = """
            {
              "text": "⚠️ *Vulnerabilities found in container file scan!*
                Severity: HIGH/CRITICAL
                Build: ${env.BUILD_URL}"
            }
            """
            sh """
              curl -X POST -H 'Content-Type: application/json' \
              -d '${message.trim()}' \
              '${webhookUrl}'
            """
            // error("Trivy scan failed due to vulnerabilities.")
            currentBuild.result = 'UNSTABLE'
          } else {
            echo "No critical vulnerabilities found."
          }
          }
        }
      }

    stage('Build Docker Image') {
      steps {
        script {
          sh """
            docker build -t rohitdarekar816/gitcommits:latest .
          """
        }
      }
    }

    stage('Compress Docker Image using slim') {
      steps {
        script {
          sh 'slim build --env "MONGO_URL=mongodb+srv://myAtlasDBUser:Rohit2023@github-webhook.p0pdz5y.mongodb.net/?retryWrites=true&w=majority&appName=Github-Webhook" rohitdarekar816/gitcommits:latest'
        }
      }
    }

    stage('rename docker image') {
      steps{
        script{
          sh 'docker tag rohitdarekar816/gitcommits.slim rohitdarekar816/gitcommits:slim'
        }
      }
    }

    stage('Scan image') {
      steps {
        script {
          def scanreportFile = 'trivy-report.json'
          sh """
            docker run --rm -v $PWD:/root/scan aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL --format json -o /root/scan/${reportFile} rohitdarekar816/gitcommits:slim
          """
          archiveArtifacts artifacts: "${scanreportFile}", fingerprint: true
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        script {
          sh 'docker push rohitdarekar816/gitcommits:slim'
        }
      }
    }

    stage('Clean docker images') {
      steps {
        script {
          sh 'docker image prune -a -f'
        }
      }
    }
  }

  post {
    success {
      steps {
        script {
          def message = "This prod_infra pipeline is success!"
          def jsonPayload = "{\"text\": \"${message}\"}"
          sh """
            curl -X POST \\
            -H "Content-Type: application/json" \\
            -d '${jsonPayload}' \\
            "https://chat.googleapis.com/v1/spaces/AAQAoL3O840/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=iqBfBelvIk5ZaQ55RhdOTR0s-IwkOVm_ZCsD23SWsbk"
          """
        }
      }
    }
    failure {
      echo 'This pipeline failed.'
    }
    always {
      echo 'This message always runs, regardless of success or failure.'
    }
  }
}

