pipeline {
    agent { label 'small' }
    environment {
      imagename = "ghcr.io/pilotdataplatform/notification"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      dockerImage = ''
    }

    stages {

    stage('DEV: Git clone') {
        when { branch 'develop' }
        steps {
            git branch: 'develop',
                url: 'https://github.com/PilotDataPlatform/notification.git',
                credentialsId: 'lzhao'
        }
    }

    stage('DEV Build and push image') {
      when {branch "develop"}
      steps {
        script {
            docker.withRegistry('https://ghcr.io', registryCredential) {
                customImage = docker.build('$imagename:alembic-$commit-CAC', '--target alembic-image .')
                customImage.push()
            }
            docker.withRegistry('https://ghcr.io', registryCredential) {
                customImage = docker.build('$imagename:notification-$commit-CAC', '--target notification-image .')
                customImage.push()
            }
        }
      }
    }

    stage('DEV Remove image') {
      when {branch "develop"}
      steps {
            sh 'docker rmi $imagename:alembic-$commit-CAC'
            sh 'docker rmi $imagename:notification-$commit-CAC'
      }
    }

    stage('DEV Deploy') {
      when {branch "develop"}
      steps{
        build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'notification' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit-CAC" ]
        ])
      }
    }
/**
    stage('STAGING: Git clone') {
        when { branch 'main' }
        steps {
            git branch: 'main',
                url: 'https://github.com/PilotDataPlatform/notification.git',
                credentialsId: 'lzhao'
        }
    }

    stage('STAGING Building and push image') {
      when {branch "main"}
      steps {
        script {
              docker.withRegistry('https://ghcr.io', registryCredential) {
                  customImage = docker.build("$imagename:$commit", ".")
                  customImage.push()
              }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "main"}
      steps{
        sh "docker rmi $imagename:$commit"
      }
    }

    stage('STAGING Deploy') {
      when {branch "main"}
      steps{
        build(job: "/VRE-IaC/Staging-UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'staging' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'notification' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }
**/
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} $commit  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }

}
