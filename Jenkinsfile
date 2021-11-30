#!groovy

@Library('jenkins_lib') _

String project = 'mlflow-client'

String docker_registry = 'docker.rep.msk.mts.ru'
String docker_image = "bigdata/platform/dsx/${project}"
String mlflow_image = 'bigdata/platform/dsx/mlflow'

Map git_info = [:]
Map version_info = [:]

List suffixes = ['unit', 'integration']
List python_versions = ['3.7', '3.8']

pipeline {
    agent {
        label 'adm-ci'
    }

    options {
        ansiColor('xterm')
        parallelsAlwaysFailFast()

        // Mandatory steps only
        gitlabBuilds(builds: [
            "Build test images",
            "Run tests",
            "Sonar Scan",
            "Build pip package",
            "Build documentation"
        ])
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    deleteDirRoot onlyContent: true

                    def scmVars = checkout scm
                    git_info = getGitInfo(scmVars)
                    version_info = getVersionInfo(git_info.tag)

                    sh script: """
                        mkdir -p ./reports/junit
                        touch ./reports/pylint.txt
                        chmod 777 -R ./reports
                    """
                }
            }
        }

        stage('Build test images') {
            matrix {
                axes {
                    axis {
                        name 'SUFFIX'
                        // TODO: replace with suffixes variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values 'unit', 'integration'
                    }
                    axis {
                        name 'PYTHON_VERSION'
                        // TODO: replace with python_versions variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values '3.7', '3.8'
                    }
                }
                stages {
                    stage('Build test images') {
                        options {
                            retry(3)
                        }

                        steps {
                            gitlabCommitStatus('Build test images') {
                                script {
                                    try {
                                        docker.image("${docker_registry}/platform/python:${env.PYTHON_VERSION}").pull()
                                        docker.image("${docker_registry}/${mlflow_image}:latest").pull()
                                    } catch (Exception e) {}

                                    docker.build("${docker_registry}/${docker_image}:${env.SUFFIX}-python${env.PYTHON_VERSION}-${env.BUILD_ID}", "--build-arg BUILD_ID=${env.BUILD_ID} --build-arg PYTHON_VERSION=${env.PYTHON_VERSION} --force-rm -f Dockerfile.${env.SUFFIX} .")
                                    docker.build("${docker_registry}/${docker_image}:${env.SUFFIX}-${env.BUILD_ID}", "--build-arg BUILD_ID=${env.BUILD_ID} --force-rm -f Dockerfile.${env.SUFFIX} .")
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Get version') {
            agent {
                docker {
                    reuseNode true
                    image "${docker_registry}/${docker_image}:unit-${env.BUILD_ID}"
                    args "--entrypoint=''"
                }
            }

            steps {
                script {
                    String raw_version = ''

                    try {
                        raw_version = sh(script: "python setup.py --version", returnStdout: true)
                    } catch (Exception e) {}

                    version_info = getVersionInfo(raw_version)
                }
            }
        }

        stage('Tag release images') {
            when {
                allOf {
                    expression { git_info.is_release }
                    expression { version_info.docker_version }
                }
            }
            matrix {
                axes {
                    axis {
                        name 'SUFFIX'
                        // TODO: replace with suffixes variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values 'unit', 'integration'
                    }
                    axis {
                        name 'PYTHON_VERSION'
                        // TODO: replace with python_versions variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values '3.7', '3.8'
                    }
                }
                stages {
                    stage('Tag release images') {
                        steps {
                            script {
                                docker.image("${docker_registry}/${docker_image}:${env.SUFFIX}-python${env.PYTHON_VERSION}-${env.BUILD_ID}").tag("${env.SUFFIX}-python${env.PYTHON_VERSION}-${version_info.docker_version}")
                            }
                        }
                    }
                }
            }
        }

        stage('Run tests') {
            matrix {
                axes {
                    axis {
                        name 'SUFFIX'
                        // TODO: replace with suffixes variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values 'unit', 'integration'
                    }
                    axis {
                        name 'PYTHON_VERSION'
                        // TODO: replace with python_versions variable after https://issues.jenkins.io/browse/JENKINS-62127
                        values '3.7', '3.8'
                    }
                }

                environment {
                    TAG = "${env.SUFFIX}-python${env.PYTHON_VERSION}-${env.BUILD_ID}"
                    COMPOSE_PROJECT_NAME = "${env.SUFFIX}-${env.BUILD_TAG}-${env.PYTHON_VERSION}"
                    COMPOSE_FILE = "docker-compose.jenkins-${env.SUFFIX}.yml"
                }

                stages {
                    stage('Run tests') {
                        steps {
                            gitlabCommitStatus('Run tests') {
                                sh script: """
                                    docker-compose run --rm mlflow-client-jenkins-${env.SUFFIX}
                                """
                            }
                        }

                        post {
                            cleanup {
                                sh script: """
                                    docker-compose down -v || true
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Prepare Sonar report data') {
            agent {
                docker {
                    reuseNode true
                    image "${docker_registry}/${docker_image}:unit-${env.BUILD_ID}"
                    args "--entrypoint='' -u root -v ${env.WORKSPACE}/reports:/app/reports"
                }
            }

            steps {
                gitlabCommitStatus('Prepare Sonar report data') {
                    sh script: """
                        # Get coverage report
                        coverage.sh
                        sed -i 's#/app#${env.WORKSPACE}#g' /app/reports/coverage*.xml

                        # Get pylint report
                        python -m pylint mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero > /app/reports/pylint.txt

                        # Get bandit report
                        python -m bandit -r mlflow_client -f json -o /app/reports/bandit.json || true
                    """
                }
            }

            post {
                always {
                    junit 'reports/junit/*.xml'
                }
            }
        }

        stage('Sonar Scan') {
            environment {
                SONAR_DB_PASSWD = credentials('SONAR_DB_PASSWD')
            }

            steps {
                gitlabCommitStatus('Sonar Scan') {
                    withSonarQubeEnv('sonarqube') {
                        script {
                            sh "/data/sonar-scanner/bin/sonar-scanner -Dsonar.projectVersion=${version_info.version}"
                        }
                    }

                    timeout(time: 15, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Build pip package') {
            steps {
                gitlabCommitStatus('Build pip package') {
                    script {
                        // We do not use matrix + docker agent because parallel wheel build is not supported
                        python_versions.each { def python_version ->
                            docker.image("${docker_registry}/${docker_image}:unit-python${python_version}-${env.BUILD_ID}").inside("--entrypoint=''") {
                                sh script: """
                                    python setup.py bdist_wheel
                                    python setup.py sdist
                                """
                            }
                        }
                    }
                }
            }
        }

        stage ('Build documentation') {
            agent {
                docker {
                    reuseNode true
                    image "${docker_registry}/${docker_image}:unit-${env.BUILD_ID}"
                    args "--entrypoint='' -u root"
                }
            }

            steps {
                gitlabCommitStatus('Build documentation') {
                    script {
                        sh script: """
                            cd docs
                            make html
                            tar cvzf html-${version_info.version}.tar.gz -C build/html .
                        """

                        if (git_info.is_release) {
                            sh script: """
                                cd docs
                                cp html-${version_info.version}.tar.gz html-latest.tar.gz
                            """
                        }
                    }
                }
            }
        }

        stage ('Publish package & documentation') {
            steps {
                gitlabCommitStatus('Publish package & documentation') {
                    rtUpload (
                        serverId: 'rep.msk.mts.ru',
                        spec: '''{
                            "files": [
                                {
                                    "pattern": "docs/html-*.tar.gz",
                                    "target": "files/mlflow-client-docs/"
                                },
                                {
                                    "pattern": "dist/.*(.tar.gz|.whl)",
                                    "target": "pypi-local/mlflow-client/",
                                    "regexp": "true"
                                }
                            ]
                        }'''
                    )

                    rtPublishBuildInfo (
                        serverId: 'rep.msk.mts.ru'
                    )
                }
            }
        }

        stage('Cleanup Artifactory') {
            steps {
                gitlabCommitStatus('Cleanup Artifactory') {
                    build job: 'artifactory-cleanup', propagate: false, parameters: [
                        string(name: 'PACKAGE_NAME', value: project),
                        string(name: 'PACKAGE_TYPE', value: 'pypi'),
                        booleanParam(name: 'REMOVE_PYPI', value: true),
                        booleanParam(name: 'REMOVE_DOCKER_IMAGES', value: false),
                        booleanParam(name: 'REMOVE_DOCS', value: true),
                        booleanParam(name: 'DRY_RUN', value: false)
                    ]
                }
            }
        }

        stage('Deploy documentation') {
            steps {
                gitlabCommitStatus('Deploy documentation') {
                    build job: 'nginx-build', parameters: [
                        string(name: 'PROJECT_NAME',  value: project),
                        string(name: 'IMAGE_NAME',    value: docker_image),
                        string(name: 'VERSION',       value: version_info.docker_version),
                        booleanParam(name: 'DRY_RUN', value: false)
                    ]
                }
            }
        }
    }

    post {
        cleanup {
            script {
                suffixes.each { String suffix ->
                    python_versions.each { def python_version ->
                        sh script: """
                            docker rmi ${docker_registry}/${docker_image}:${suffix}-python${python_version}-${env.BUILD_ID} || true
                        """
                    }

                    sh script: """
                        docker rmi ${docker_registry}/${docker_image}:${suffix}-${env.BUILD_ID} || true
                    """
                }

                deleteDirRoot()
            }
        }
    }
}
