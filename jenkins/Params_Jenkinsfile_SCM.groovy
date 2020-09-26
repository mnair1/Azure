pipeline {
    agent any
    parameters {
        string(name: 'CODEBUILD_PROJ_NAME', defaultValue: '', description: 'CodeBuild Project Name')
        string(name: 'ARTIFACTS_BUCKET_NAME', defaultValue: '', description: 'Name of S3 Artifacts Bucket')
    }
    environment { 
        ARTIFACT_NAME = "artifact.zip"
        ARTIFACTS_FOLDER = "jenkins_artifacts"
        SOURCE_ARTIFACTS_PATH = "source_artifacts"
        BUILD_ARTIFACTS_PATH = "build_artifacts"
        BUILDSPEC_PATH = "jenkins/build/buildspec.yml"
        CODEBUILD_CREDENTIALS = "${env.CODEBUILD_CREDENTIALS_ID}"
        REGION = "${env.AWS_REGION}"

        MONGO_DB = "datafencedb"
        MONGO_HOST = "localhost"
        MONGO_PORT = "27017"
        FLASK_HOST = "localhost"
        FLASK_PORT = "5000"
        VERSION_AXIOS = "^0.18.0"
        VERSION_REACT = "^16.5.1"
        VERSION_REACT_DOM = "^16.5.1"
        VERSION_REACT_SCRIPTS = "1.1.5"

        JENKINS_DIRECTORY = "jenkins"
        MULTI_TIER_APP_DIRECTORY = "${JENKINS_DIRECTORY}/multi-tier-app"

    }
    stages { 
        
        stage('Pre-Build') {
            
            steps {
                dir("$MULTI_TIER_APP_DIRECTORY") {
                    echo "list the directory"
                    echo "list multi tier app directory"
                    sh 'ls'

                    echo "Updating Python Code with Specs"
                    sh "sed -i 's/<MONGO_DB>/$MONGO_DB/g' mongo.py"
                    sh "sed -i 's/<MONGO_HOST>/$MONGO_HOST/g' mongo.py"
                    sh "sed -i 's/<MONGO_PORT>/$MONGO_PORT/g' mongo.py"
                    
                    echo "Updating NodeJs config with Specs"
                    sh "sed -i 's/<VERSION_AXIOS>/$VERSION_AXIOS/g' package.json"
                    sh "sed -i 's/<VERSION_REACT>/$VERSION_REACT/g' package.json"
                    sh "sed -i 's/<VERSION_REACT_DOM>/$VERSION_REACT_DOM/g' package.json"
                    sh "sed -i 's/<VERSION_REACT_SCRIPTS>/$VERSION_REACT_SCRIPTS/g' package.json"
                    sh "sed -i 's/<FLASK_HOST>/$FLASK_HOST/g' package.json"
                    sh "sed -i 's/<FLASK_PORT>/$FLASK_PORT/g' package.json"
                    
                    sh "cat package.json"
                    sh "cat mongo.py"
                }

                // echo "list the directory"
                // sh 'ls'
                // // sh 'cd codepipeline/multi-tier-app'
                // echo "list multi tier app directory"
                // sh 'ls $MULTI_TIER_APP_DIRECTORY'

                // echo "Existing Python code"
                // sh 'cat $MULTI_TIER_APP_DIRECTORY/mongo.py'
                // echo "Updating Python Code with Specs"
                // sh "sed -i 's/<MONGO_DB>/$MONGO_DB/g' $MULTI_TIER_APP_DIRECTORY/mongo.py"
                // sh "sed -i 's/<MONGO_HOST>/$MONGO_HOST/g' $MULTI_TIER_APP_DIRECTORY/mongo.py"
                // sh "sed -i 's/<MONGO_PORT>/$MONGO_PORT/g' $MULTI_TIER_APP_DIRECTORY/mongo.py"
                // //sh "cat mongo.py"

                // echo "Existing Package.json"
                // sh "cat $MULTI_TIER_APP_DIRECTORY/package.json"
                // echo "Updating NodeJs config with Specs"
                // sh "sed -i 's/<VERSION_AXIOS>/$VERSION_AXIOS/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "sed -i 's/<VERSION_REACT>/$VERSION_REACT/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "sed -i 's/<VERSION_REACT_DOM>/$VERSION_REACT_DOM/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "sed -i 's/<VERSION_REACT_SCRIPTS>/$VERSION_REACT_SCRIPTS/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "sed -i 's/<FLASK_HOST>/$FLASK_HOST/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "sed -i 's/<FLASK_PORT>/$FLASK_PORT/g' $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "cat $MULTI_TIER_APP_DIRECTORY/package.json"
            }
        }
        stage('Build') {
            agent {
                docker { 
                    image 'node:12' 
                    args '-v /var/jenkins_home/workspace/${JOB_NAME}:/datafence'

                }
            }
            steps {
                // echo "${JOB_NAME}"
                // sh "pwd"
                // sh "ls"
                sh "ls /datafence"
                dir("/datafence/$MULTI_TIER_APP_DIRECTORY") {
                    
                    sh "cat package.json"
                    echo "Node Version"
                    sh 'npm --version'
                    sh 'npm install'
                    
                }
                // sh "cat /datafence/jenkins/multi-tier-app/package.json"
                // echo "Node Version"
                // sh 'node --version'
                // sh 'npm --version'
                
                
                // echo "Build Started at `date`"
                // sh 'cd /datafence/jenkins/multi-tier-app/ && npm install'
                // echo "Build Completed at `date`"

                
            }
             }
        stage('Post-Build') {
            
            steps {
                dir("$MULTI_TIER_APP_DIRECTORY") {
                    sh "ls"
                    sh "cat package.json"
                    sh "cat mongo.py"
                    echo "Compressing the artifacts"
                    sh 'tar -czvf app-artifact.zip .'
                    sh "ls"
                }
                // sh "cat $MULTI_TIER_APP_DIRECTORY/package.json"
                // sh "cat $MULTI_TIER_APP_DIRECTORY/mongo.py"
                // sh "ls $MULTI_TIER_APP_DIRECTORY/"
                // echo "Compressing the artifacts"
                // sh 'cd $MULTI_TIER_APP_DIRECTORY/ && tar -czvf app-artifact.zip .'
                // sh 'ls $MULTI_TIER_APP_DIRECTORY/'
                // sh 'cat $MULTI_TIER_APP_DIRECTORY/mongo.py'
                // sh 'cat $MULTI_TIER_APP_DIRECTORY/package.json'
                
                sh "mkdir artifacts_folder"
                
                sh 'cp $JENKINS_DIRECTORY/deploy/appspec.yml artifacts_folder/'
                sh 'cp $JENKINS_DIRECTORY/deploy/uncompress artifacts_folder/'
                sh 'cp $JENKINS_DIRECTORY/deploy/start_flask artifacts_folder/'
                sh 'cp $JENKINS_DIRECTORY/deploy/start_node artifacts_folder/'
                sh 'cp $MULTI_TIER_APP_DIRECTORY/app-artifact.zip artifacts_folder/'
                
                sh 'ls build_artifacts'
                
                // sh 'cp $JENKINS_DIRECTORY/deploy/appspec.yml .'
                // sh 'cp $JENKINS_DIRECTORY/deploy/uncompress .'
                // sh 'cp $JENKINS_DIRECTORY/deploy/start_flask .'
                // sh 'cp $JENKINS_DIRECTORY/deploy/start_node .'

                // sh 'ls'
                // sh 'mkdir build_artifacts'
                // sh 'cp app-artifact.zip build_artifacts/'
                // sh 'cp appspec.yml build_artifacts/'
                // sh 'cp uncompress build_artifacts/'
                // sh 'cp start_flask build_artifacts/'
                // sh 'cp start_node build_artifacts/'
                
            }
        }
        // stage('Build') {
        //     agent any
        //     steps {
        //     awsCodeBuild  artifactLocationOverride: params.ARTIFACTS_BUCKET_NAME, artifactNameOverride: env.ARTIFACT_NAME, artifactPackagingOverride: 'ZIP', artifactPathOverride: "${env.ARTIFACTS_FOLDER}/${env.BUILD_ARTIFACTS_PATH}/", artifactTypeOverride: 'S3', awsAccessKey: env.AWS_ACCESS_KEY_ID, awsSecretKey: env.AWS_SECRET_ACCESS_KEY, buildSpecFile: env.BUILDSPEC_PATH, cloudWatchLogsGroupNameOverride: '', cloudWatchLogsStatusOverride: 'ENABLED', cloudWatchLogsStreamNameOverride: '', computeTypeOverride: '', credentialsId: env.CODEBUILD_CREDENTIALS, credentialsType: 'jenkins', cwlStreamingDisabled: '', downloadArtifacts: 'false', downloadArtifactsRelativePath: '', envParameters: '', envVariables: '', environmentTypeOverride: '', localSourcePath: '', overrideArtifactName: '', privilegedModeOverride: '', projectName: params.CODEBUILD_PROJ_NAME, proxyHost: '', region: env.REGION, serviceRoleOverride: '', sourceControlType: 'jenkins', sourceLocationOverride: "${params.ARTIFACTS_BUCKET_NAME}/${env.ARTIFACTS_FOLDER}/${env.SOURCE_ARTIFACTS_PATH}/${env.ARTIFACT_NAME}", sourceTypeOverride: 'S3', sourceVersion: '', workspaceSubdir: ''
        // }
        // }
        
    }
}
