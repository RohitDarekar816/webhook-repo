pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        echo 'This is a Build stage.'
      }
    }

    stage('Test') {
      steps {
        echo 'This is a Test stage.'
      }
    }

    stage('Deploy') {
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

