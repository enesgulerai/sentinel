pipeline {
    agent any

    environment {
        REGISTRY = "ghcr.io/enesgulerdev"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        GHCR_CREDENTIALS_ID = "github-ghcr-token"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully.'
            }
        }

        stage('Build Images') {
            steps {
                echo 'Building Sentinel API and Validator images...'
                sh 'docker build -t ${REGISTRY}/sentinel-api:${IMAGE_TAG} -f docker/api/Dockerfile .'
                sh 'docker build -t ${REGISTRY}/sentinel-validator:${IMAGE_TAG} -f docker/validator/Dockerfile .'
            }
        }

        stage('Push to GHCR') {
            steps {
                echo 'Authenticating and pushing images to GitHub Container Registry...'
                withCredentials([usernamePassword(credentialsId: env.GHCR_CREDENTIALS_ID, usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_PAT')]) {
                    sh 'echo $GHCR_PAT | docker login ghcr.io -u $GHCR_USER --password-stdin'

                    sh 'docker push ${REGISTRY}/sentinel-api:${IMAGE_TAG}'
                    sh 'docker push ${REGISTRY}/sentinel-validator:${IMAGE_TAG}'
                }
            }
        }
    }
}
