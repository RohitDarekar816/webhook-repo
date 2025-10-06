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

    stage('Compress Docker Image') {
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
          sh 'slim --env "MONGO_URL=mongodb+srv://myAtlasDBUser:Rohit2023@github-webhook.p0pdz5y.mongodb.net/?retryWrites=true&w=majority&appName=Github-Webhook" build rohitdarekar816/gitcommits:latest'
          echo 'List docker images'
          sh 'docker images'
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
  }

  post {
    success {
      echo 'This pipeline completed successfully.'
    }
    failure {
      echo 'This pipeline failed.'
    }
    always {
      echo 'This message always runs, regardless of success or failure.'
    }
  }
}

