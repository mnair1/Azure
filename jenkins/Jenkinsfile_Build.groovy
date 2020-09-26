pipeline {
    agent any
    
    environment { 
        
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
        
        stage('Update_Configurations') {
            
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
    }
}
