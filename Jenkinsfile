pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        awsCodeBuild 'test'
      }
    }

    stage('Deploy') {
      steps {
        sh 'ls'
      }
    }

  }
}