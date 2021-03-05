pipeline {
    agent any
    parameters {
        string(name: 'CODEBUILD_PROJ_NAME', defaultValue: 'devops-df-jenkins-build-project', description: 'CodeBuild Project Name')
        string(name: 'ARTIFACTS_BUCKET_NAME', defaultValue: 'devops-df-cicd-artifact-bucket-jenkins-syed', description: 'Name of S3 Artifacts Bucket')
    }
    environment { 
        ARTIFACT_NAME = "artifact.zip"
        ARTIFACTS_FOLDER = "jenkins_artifacts"
        SOURCE_ARTIFACTS_PATH = "source_artifacts"
        BUILD_ARTIFACTS_PATH = "build_artifacts"
        BUILDSPEC_PATH = "jenkins/build/buildspec.yml"
        CODEBUILD_CREDENTIALS = "${env.CODEBUILD_CREDENTIALS_ID}"
        REGION = "${env.AWS_REGION}"

        JENKINS_DIRECTORY = "jenkins"
        MULTI_TIER_APP_DIRECTORY = "${JENKINS_DIRECTORY}/multi-tier-app"

    }
    stages { 
        
        stage('Build') {
            agent any
            steps {
            awsCodeBuild  artifactLocationOverride: params.ARTIFACTS_BUCKET_NAME, artifactNameOverride: env.ARTIFACT_NAME, artifactPackagingOverride: 'ZIP', artifactPathOverride: "${env.ARTIFACTS_FOLDER}/${env.BUILD_ARTIFACTS_PATH}/", artifactTypeOverride: 'S3', awsAccessKey: '', awsSecretKey: '', buildSpecFile: env.BUILDSPEC_PATH, cloudWatchLogsGroupNameOverride: '', cloudWatchLogsStatusOverride: 'ENABLED', cloudWatchLogsStreamNameOverride: '', computeTypeOverride: '', credentialsId: env.CODEBUILD_CREDENTIALS, credentialsType: 'jenkins', cwlStreamingDisabled: '', downloadArtifacts: 'false', downloadArtifactsRelativePath: '', envParameters: '', envVariables: '', environmentTypeOverride: '', localSourcePath: '', overrideArtifactName: '', privilegedModeOverride: '', projectName: params.CODEBUILD_PROJ_NAME, proxyHost: '', region: env.REGION, serviceRoleOverride: '', sourceControlType: 'jenkins', sourceLocationOverride: "${params.ARTIFACTS_BUCKET_NAME}/${env.ARTIFACTS_FOLDER}/${env.SOURCE_ARTIFACTS_PATH}/${env.ARTIFACT_NAME}", sourceTypeOverride: 'S3', sourceVersion: '', workspaceSubdir: ''
        }
        }
        
    }
}