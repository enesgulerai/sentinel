pipeline {
    agent any

    environment {
        REGISTRY = "ghcr.io/enesgulerdev"
        GHCR_CREDENTIALS_ID = "github-ghcr-token"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
                echo "Source code checked out successfully. Target Git SHA: ${env.IMAGE_TAG}"
            }
        }

        stage('Build Images') {
            steps {
                echo 'Building Sentinel API, Validator, and Consumer images...'
                sh 'docker build -t ${REGISTRY}/sentinel-api:${IMAGE_TAG} -f docker/api/Dockerfile .'
                sh 'docker build -t ${REGISTRY}/sentinel-validator:${IMAGE_TAG} -f docker/validator/Dockerfile .'
                sh 'docker build -t ${REGISTRY}/sentinel-consumer:${IMAGE_TAG} -f docker/consumer/Dockerfile .'
            }
        }

        stage('Push to GHCR') {
            steps {
                echo 'Authenticating and pushing images to GitHub Container Registry...'
                withCredentials([usernamePassword(credentialsId: env.GHCR_CREDENTIALS_ID, usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_PAT')]) {
                    sh 'echo $GHCR_PAT | docker login ghcr.io -u $GHCR_USER --password-stdin'

                    sh 'docker push ${REGISTRY}/sentinel-api:${IMAGE_TAG}'
                    sh 'docker push ${REGISTRY}/sentinel-validator:${IMAGE_TAG}'
                    sh 'docker push ${REGISTRY}/sentinel-consumer:${IMAGE_TAG}'
                }
            }
        }

        stage('Update GitOps Manifests') {
            steps {
                echo 'Updating Helm values.yaml with the new image tags...'
                script {
                    sh """
                        sed -i '/repository: ghcr.io\\/enesgulerdev\\/sentinel-/!b;n;s/tag: .*/tag: ${IMAGE_TAG}/' infrastructure/helm/sentinel/values.yaml
                    """

                    // Configure Git as Jenkins user
                    sh "git config user.email 'jenkins@sentinel.local'"
                    sh "git config user.name 'Jenkins CI'"

                    // Commit and push the changes back to GitHub
                    sh "git add infrastructure/helm/sentinel/values.yaml"
                    sh "git commit -m 'chore(gitops): auto-update image tags to ${IMAGE_TAG} [skip ci]'"

                    withCredentials([usernamePassword(credentialsId: env.GHCR_CREDENTIALS_ID, usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_PAT')]) {
                        sh "git push https://${GHCR_USER}:${GHCR_PAT}@github.com/enesgulerdev/sentinel.git HEAD:main"
                    }
                }
            }
        }
    }
}
