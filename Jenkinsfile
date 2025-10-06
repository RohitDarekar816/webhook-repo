pipeline {
  agent any

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

    stage('Build') {
      steps {
        script {
          sh """
            docker build -t rohitdarekar816/gitcommits:jen1 .
          """
        }
      }
    }

    stage('Push to Dockier Hub') {
      steps {
        echo 'This is a Deploy stage.'
      }
    }

    stage('Notification') {
      steps {
        echo 'Notification sent'
        echo 'Notification to Google Chats'
        echo 'This is an email notification'
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

