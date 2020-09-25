pipeline {
    agent any
    parameters {
        string(name: 'GITHUB_REPO_BRANCH', defaultValue: "", description: 'GitHub Branch Name')
        string(name: 'GITHUB_CREDENTIALS_ID', defaultValue: "${env.GITHUB_CREDENTIALS_ID}", description: 'GitHub Jenkins Credentials ID')
        string(name: 'GITHUB_REPO_URL', defaultValue: '', description: 'URL of GitHub Repo')
        string(name: 'CODEBUILD_PROJ_NAME', defaultValue: '', description: 'CodeBuild Project Name')
        string(name: 'CODEBUILD_CREDENTIALS_ID', defaultValue: "${env.CODEBUILD_CREDENTIALS_ID}", description: 'Jenkins Credentials ID for CodeBuild')
    }
    // environment { 
        
    // }
    stages { 
        
        stage('Code Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: "${params.GITHUB_REPO_BRANCH}"]], 
                    userRemoteConfigs: [[url: "${params.GITHUB_REPO_URL}", credentialsId: "${params.GITHUB_CREDENTIALS_ID}"]]
                ])
            }
        }
        
        stage('Build') {
            steps {
            awsCodeBuild artifactEncryptionDisabledOverride: '', artifactLocationOverride: 'devops-df-cicd-artifact-bucket-jenkins-syed', artifactNameOverride: 'artifact.zip', artifactNamespaceOverride: '', artifactPackagingOverride: 'ZIP', artifactPathOverride: 'jenkins_artifacts/build_artifacts/', artifactTypeOverride: 'S3', awsAccessKey: env.AWS_ACCESS_KEY_ID, awsSecretKey: env.AWS_SECRET_ACCESS_KEY, buildSpecFile: '', buildTimeoutOverride: '', cacheLocationOverride: '', cacheModesOverride: '', cacheTypeOverride: '', certificateOverride: '', cloudWatchLogsGroupNameOverride: '', cloudWatchLogsStatusOverride: 'ENABLED', cloudWatchLogsStreamNameOverride: '', computeTypeOverride: '', credentialsId: "${params.CODEBUILD_CREDENTIALS_ID}", credentialsType: 'jenkins', cwlStreamingDisabled: '', downloadArtifacts: 'false', downloadArtifactsRelativePath: '', envParameters: '', envVariables: '', environmentTypeOverride: '', exceptionFailureMode: '', gitCloneDepthOverride: '', imageOverride: '', insecureSslOverride: '', localSourcePath: '', overrideArtifactName: '', privilegedModeOverride: '', projectName: "${params.CODEBUILD_PROJ_NAME}", proxyHost: '', proxyPort: '', region: 'us-east-1', reportBuildStatusOverride: '', s3LogsEncryptionDisabledOverride: '', s3LogsLocationOverride: '', s3LogsStatusOverride: '', secondaryArtifactsOverride: '', secondarySourcesOverride: '', secondarySourcesVersionOverride: '', serviceRoleOverride: '', sourceControlType: 'jenkins', sourceLocationOverride: 'devops-df-cicd-artifact-bucket-jenkins-syed/jenkins_artifacts/source_artifacts/artifact.zip', sourceTypeOverride: 'S3', sourceVersion: '', sseAlgorithm: '', workspaceSubdir: ''
        }
        }
        
    }
}
