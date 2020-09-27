pipeline {
    agent any
    parameters {
        string(name: 'MONGO_DB', defaultValue: 'datafencedb', description: 'Mongo DB Name')
        string(name: 'MONGO_HOST', defaultValue: 'localhost', description: 'Hostname of Mongo DB')
        string(name: 'MONGO_PORT', defaultValue: '27017', description: 'Port of Mongo DB')
        string(name: 'FLASK_HOST', defaultValue: 'localhost', description: 'Hostname of Flask')
        string(name: 'FLASK_PORT', defaultValue: '5000', description: 'Port of Flask')
        string(name: 'VERSION_AXIOS', defaultValue: '^0.18.0', description: 'Version of Axios')
        string(name: 'VERSION_REACT', defaultValue: '^16.5.1', description: 'Version of React')
        string(name: 'VERSION_REACT_DOM', defaultValue: '^16.5.1', description: 'Version of React DOM')
        string(name: 'VERSION_REACT_SCRIPTS', defaultValue: '1.1.5', description: 'Version of React Scripts')
        
        string(name: 'ARTIFACTS_BUCKET_NAME', defaultValue: 'devops-df-cicd-artifact-bucket-jenkins-syed', description: 'Name of S3 Artifacts Bucket')
        string(name: 'CODEDEPLOY_APP', defaultValue: 'devops-df-cicd-app', description: 'CodeDeploy Application Name')
        string(name: 'CODEDEPLOY_DEP_GRP', defaultValue: 'multi-tier-app', description: 'CodeDeploy Deployment Group Name')
    }
    environment { 

        JENKINS_DIRECTORY = "jenkins"
        MULTI_TIER_APP_DIRECTORY = "${JENKINS_DIRECTORY}/multi-tier-app"

        AWS_ACCESS_KEY_ID     = credentials('AWS_Access_Key')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_Secret_Key')
        REGION = "${env.AWS_REGION}"
        
        ARTIFACTS_FOLDER = "jenkins_artifacts"
        DEPLOY_ARTIFACTS_PATH = "deploy_artifacts"
        ARTIFACT_NAME = "artifact.zip"
    }
    stages { 
        
        stage('Update_Configurations') {
            
            steps {
                dir("$MULTI_TIER_APP_DIRECTORY") {
                    echo "list the directory"
                    echo "list multi tier app directory"
                    sh 'ls'

                    echo "Updating Python Code with Specs"
                    sh "sed -i 's/<MONGO_DB>/${params.MONGO_DB}/g' mongo.py"
                    sh "sed -i 's/<MONGO_HOST>/${params.MONGO_HOST}/g' mongo.py"
                    sh "sed -i 's/<MONGO_PORT>/${params.MONGO_PORT}/g' mongo.py"
                    
                    echo "Updating NodeJs config with Specs"
                    sh "sed -i 's/<VERSION_AXIOS>/${params.VERSION_AXIOS}/g' package.json"
                    sh "sed -i 's/<VERSION_REACT>/${params.VERSION_REACT}/g' package.json"
                    sh "sed -i 's/<VERSION_REACT_DOM>/${params.VERSION_REACT_DOM}/g' package.json"
                    sh "sed -i 's/<VERSION_REACT_SCRIPTS>/${params.VERSION_REACT_SCRIPTS}/g' package.json"
                    sh "sed -i 's/<FLASK_HOST>/${params.FLASK_HOST}/g' package.json"
                    sh "sed -i 's/<FLASK_PORT>/${params.FLASK_PORT}/g' package.json"
                    
                    sh "cat package.json"
                    sh "cat mongo.py"
                }
            }
        }
        stage('Build') {
            agent {
                docker { 
                    image 'node:12' 
                    args "-v /var/jenkins_home/workspace/${JOB_NAME}:/datafence"

                }
            }
            steps {
                echo "Node Version"
                sh 'npm --version'
                
                sh "ls /datafence"
                sh "cat /datafence/${MULTI_TIER_APP_DIRECTORY}/package.json"
                sh "cd /datafence/${MULTI_TIER_APP_DIRECTORY} && npm install"   
            }
             }
        stage('Artifact_Creation') {
            
            steps {
                dir("$MULTI_TIER_APP_DIRECTORY") {
                    sh "ls"
                    sh "cat package.json"
                    sh "cat mongo.py"
                    echo "Compressing the artifacts"
                    sh 'tar -czvf app-artifact.tar.gz .'
                    sh "ls"
                }
                
                sh "mkdir -p build_artifact"
                
                sh 'cp $JENKINS_DIRECTORY/deploy/appspec.yml build_artifact/'
                sh 'cp $JENKINS_DIRECTORY/deploy/uncompress build_artifact/'
                sh 'cp $JENKINS_DIRECTORY/deploy/start_flask build_artifact/'
                sh 'cp $JENKINS_DIRECTORY/deploy/start_node build_artifact/'
                sh 'cp $MULTI_TIER_APP_DIRECTORY/app-artifact.tar.gz build_artifact/'
                sh 'ls build_artifact'
                
            }
        }
        // stage('Approval') {
        //     input {
        //         message "Want to proceed with the deployment"
        //         ok "Yes"
        //     }
        //     steps {
        //         sh "Build has been approved"
        //     }
            
        // }
        stage('Deploy') {
            
            input {
                message "Want to proceed with the deployment"
                ok "Yes"
            }
            
            steps {
                step([$class: 'AWSCodeDeployPublisher', applicationName: "${params.CODEDEPLOY_APP}", awsAccessKey: "${AWS_ACCESS_KEY_ID}", awsSecretKey: "${AWS_SECRET_ACCESS_KEY}", credentials: 'awsAccessKey', deploymentGroupAppspec: false, deploymentGroupName: "${params.CODEDEPLOY_DEP_GRP}", deploymentMethod: 'deploy', excludes: '', iamRoleArn: '', includes: '**', proxyHost: '', proxyPort: 0, region: "${REGION}", s3bucket: "${params.ARTIFACTS_BUCKET_NAME}", s3prefix: "${ARTIFACTS_FOLDER}/${DEPLOY_ARTIFACTS_PATH}", subdirectory: 'build_artifact', versionFileName: "${ARTIFACT_NAME}", waitForCompletion: false])
            }
        }
    }
}
