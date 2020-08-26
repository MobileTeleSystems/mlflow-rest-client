#!groovy

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

String git_tag
String git_branch
String git_commit

Boolean isMaster = false
Boolean isDev = true
Boolean isRelease = false

String testTag
String version

List pythonVersions = ['2.7', '3.6', '3.7']

node('bdbuilder04') {
    try {
        gitlabBuilds(builds: ["Build test images", "Run integration tests", "Check coverage", "Pylint", "Sonar Scan", "Retrieve Sonar Results", "Deploy test images", "Build pip package", "Building documentation", "Publishing package to Artifactory", "Build and push nginx docs images"]) {
            stage('Checkout') {
                def scmVars = checkout scm
                git_tag = sh(script: "git describe --tags --abbrev=0 --exact-match || exit 0", returnStdout: true).trim()
                if (git_tag == 'null' || git_tag == '') {
                    git_tag = null
                }
                git_branch = scmVars.GIT_BRANCH.replace('origin/', '').replace('feature/', '').trim()
                git_commit = scmVars.GIT_COMMIT

                println(git_tag)
                println(git_branch)
                println(git_commit)

                sh script: """
                    mkdir -p ./reports/junit
                    touch ./reports/pylint.txt
                """
            }

            isMaster  = git_branch == 'master'
            isDev     = git_branch == 'dev'
            isRelease = isMaster && git_tag
            version   = git_tag

            testTag = isMaster ? 'test' : 'dev-test'

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    def build = [
                        failFast: true
                    ]

                    withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                        pythonVersions.each{ def pythonVersion ->
                            def testTagVersioned = "${testTag}-python${pythonVersion}"

                            build[pythonVersion] = {
                                ansiColor('xterm') {
                                    try {
                                        // Fetch cache
                                        cache = docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTagVersioned}").pull()
                                    } catch (Exception e) {}

                                    docker.build("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTagVersioned}-${env.BUILD_TAG}", "--build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .")
                                }
                            }
                        }
                        parallel build

                        ansiColor('xterm') {
                            try {
                                // Fetch cache
                                docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTag}").pull()
                            } catch (Exception e) {}

                            docker.build("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTag}-${env.BUILD_TAG}", "--force-rm -f Dockerfile.test .")
                        }
                    }
                }
            }

            stage('Run integration tests') {
                gitlabCommitStatus('Run integration tests') {
                    def build = [
                        failFast: true
                    ]
                    pythonVersions.each{ def pythonVersion ->
                        build[pythonVersion] = {
                            withEnv(["TAG=${testTag}-python${pythonVersion}-${env.BUILD_TAG}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}-${pythonVersion}" run --rm mlflow-client-jenkins
                                        docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}-${pythonVersion}" down
                                    """
                                }
                            }
                        }
                    }
                    parallel build
                }
            }

            stage('Check coverage') {
                gitlabCommitStatus('Check coverage') {
                    withEnv(["TAG=${testTag}-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" run --rm --no-deps mlflow-client-jenkins coverage.sh
                                docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" down
                            """
                        }
                    }
                    
                    junit 'reports/junit/*.xml'
                }
            }

            stage('Pylint') {
                gitlabCommitStatus('Pylint') {
                    withEnv(["TAG=${testTag}-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" run --rm --no-deps mlflow-client-jenkins bash -c 'python -m pylint .mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                                docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" down
                            """
                        }
                    }
                }
            }

            stage('Sonar Scan') {
                gitlabCommitStatus('Sonar Scan') {
                    withSonarQubeEnv('sonarqube') {
                        withCredentials([string(credentialsId: 'SONAR_DB_PASSWD', variable: 'SONAR_DB_PASSWD')]) {
                            ansiColor('xterm') {
                                sh "/data/sonar-scanner/bin/sonar-scanner"
                            }
                        }
                    }
                }
            }

            stage('Retrieve Sonar Results') {
                gitlabCommitStatus('Retrieve Sonar Results') {
                    timeout(time: 15, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }

            stage('Deploy test images') {
                gitlabCommitStatus('Deploy test images') {
                    if (isDev || isRelease) {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            ansiColor('xterm') {
                                pythonVersions.each{ def pythonVersion ->
                                    def testTagVersioned = "${testTag}-python${pythonVersion}"

                                    docker.build("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTagVersioned}", "--build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .").push()
                                }

                                docker.build("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTag}", "--force-rm -f Dockerfile.test .").push()
                            }
                        }
                    }
                }
            }

            stage('Build pip package') {
                gitlabCommitStatus('Build pip package') {
                    if (isDev || isRelease) {
                        //Build wheels for each version
                        pythonVersions.each{ def pythonVersion ->
                            def testTagVersioned = "${testTag}-python${pythonVersion}-${env.BUILD_TAG}"

                            docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTagVersioned}").inside() {
                                ansiColor('xterm') {
                                    sh script: """
                                        python setup.py bdist_wheel sdist
                                    """
                                }
                            }
                        }
                    }
                }
            }

            stage ('Building documentation') {
                gitlabCommitStatus('Building documentation') {
                    docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTag}-${env.BUILD_TAG}").inside() {
                        try {
                            version = sh script: "python setup.py --version", returnStdout: true
                            version = version.trim()
                        } catch (Exception e) {}
                    }

                    if (isRelease) {
                        docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:${testTag}-${env.BUILD_TAG}").inside() {
                            /*
                            ansiColor('xterm') {
                                sh script: """
                                    sphinx-multiversion docs docs/build
                                    mv docs/build/master docs/build/latest
                                    tar cvzf docs/html-latest.tar.gz -C docs/build/master .
                                """
                            }
                            */
                            // Uncomment block above and remove block below after fixing https://github.com/Holzhaus/sphinx-multiversion/issues/17
                            ansiColor('xterm') {
                                sh script: """
                                    cd docs
                                    make html
                                    tar cvzf html-latest.tar.gz -C build/html .
                                    cp html-latest.tar.gz html-${version}.tar.gz
                                """
                            }
                        }

                        def uploadSpec = '''{
                                "files": [
                                    {
                                        "pattern": "docs/html-*.tar.gz",
                                        "target": "files/mlflow-client-docs/"
                                    }
                                ]
                            }'''

                        def buildInfo = server.upload spec: uploadSpec
                        server.publishBuildInfo buildInfo
                    }
                }
            }

            stage('Publishing package to Artifactory') {
                gitlabCommitStatus('Publishing package to Artifactory') {
                    if (isRelease) {
                        def uploadSpec = '''{
                                "files": [
                                    {
                                        "pattern": "dist/.*(.tar.gz|.whl)",
                                        "target": "pypi-local/mlflow-client/",
                                        "regexp": "true"
                                    }
                                ]
                            }'''

                        def buildInfo = server.upload spec: uploadSpec
                        server.publishBuildInfo buildInfo
                    }
                }
            }

            stage('Build and push nginx docs images') {
                gitlabCommitStatus('Build and push nginx docs images') {
                    if (isRelease) {
                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    // Fetch cache
                                    docker.image("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client.nginx:latest").pull()
                                } catch (Exception e) {}

                                def docs_image = docker.build("docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client.nginx:latest", "--force-rm -f ./docs/nginx/Dockerfile_nginx .")
                                docs_image.push()
                                docs_image.push(version)
                            }
                        }
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
            pythonVersions.each{ def pythonVersion ->
                withEnv(["TAG=${testTag}-python${pythonVersion}-${env.BUILD_TAG}"]) {
                    ansiColor('xterm') {
                        sh script: """
                            docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}-${pythonVersion}" down || true
                            docker rmi docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:\$TAG
                        """
                    }
                }
            }

            ansiColor('xterm') {
                withEnv(["TAG=${testTag}-${env.BUILD_TAG}"]) {
                    sh script: """
                        docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" down || true
                        docker rmi docker.rep.msk.mts.ru/bigdata/platform/dsx/mlflow-client:\$TAG
                    """
                }
            }

            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('platform/python:2.7').inside("-u root") {
                ansiColor('xterm') {
                    sh script: ''' \
                        rm -rf .[A-z0-9]*
                        rm -rf *
                    ''', returnStdout: true
                }
            }
            deleteDir()
        }
    }
}

if (isRelease) {
    gitlabCommitStatus(name: 'Deploying the documentation to the nginx server') {
        node('bdbuilder04'){
            stage ('Deploying the documentation') {
                checkout scm

                ansiblePlaybook(
                    playbook: './docs/ansible/nginx_deployment.yml',
                    inventory: './docs/ansible/inventory.ini',
                    extraVars: [
                        target_host: "test_mlflow",
                    image_version: version
                    ],
                    extras: '-vv'
                )
            }
        }
    }
}