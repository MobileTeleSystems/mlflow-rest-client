#!groovy

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

node('bdbuilder04') {
    try {
        gitlabBuilds(builds: ["Build test images", "Run unit tests", "Check coverage", "Pylint", "Sonar Scan", "Retrieve Sonar Results", "Deploy test images", "Build pip package", "Publishing documentation", "Publishing package to Artifactory"]) {
            stage('Checkout') {
                def scmVars = checkout scm
                env.GIT_TAG = "${scmVars.GIT_TAG}".trim() != 'null' ? scmVars.GIT_TAG.trim() : null
                env.GIT_BRANCH = scmVars.GIT_BRANCH.replace('origin/', '').replace('feature/', '').trim()
                env.GIT_COMMIT = scmVars.GIT_COMMIT

                sh script: """
                    mkdir -p ./reports/junit
                    touch ./reports/pylint.txt
                """
            }

            Boolean isMaster  = env.GIT_BRANCH == 'master'
            Boolean isDev     = env.GIT_BRANCH == 'dev'
            Boolean isRelease = isMaster && env.GIT_TAG

            String testTag = isMaster ? 'test'   : 'dev-test'

            List pythonVersions = ['2.7', '3.6', '3.7']

            //TODO: remove
            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                def cache = docker.image("docker.rep.msk.mts.ru/platform/python:3.7.7")
                cache.push()
                cache.pull('3.7')
            }
            //TODO

            List test_images = []

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    pythonVersions.each{ def version ->
                        def testTagVersioned = "${testTag}-python${version}"

                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                def cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}")
                                cache.pull()

                                test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}", "--build-arg PYTHON_VERSION=${version} --force-rm -f Dockerfile.test .")
                            }
                        }
                    }
                    ansiColor('xterm') {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            def cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}")
                            cache.pull()

                            test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTag}", "--force-rm -f Dockerfile.test .")
                        }
                    }
                }
            }

            stage('Run unit tests') {
                gitlabCommitStatus('Run unit tests') {
                    pythonVersions.each{ def version ->
                        withEnv(["TAG=${testTag}-python${version}"]) {
                            ansiColor('xterm') {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins.yml run --rm mlflow-client-jenkins
                                    docker-compose -f docker-compose.jenkins.yml down
                                """
                            }
                        }
                    }
                }
            }

            stage('Check coverage') {
                gitlabCommitStatus('Check coverage') {
                    withEnv(["TAG=${testTag}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins coverage.sh
                                docker-compose -f docker-compose.jenkins.yml down
                            """

                            junit 'reports/junit/*.xml'
                        }
                    }
                }
            }

            stage('Pylint') {
                gitlabCommitStatus('Pylint') {
                    withEnv(["TAG=${testTag}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins 'pylint .bin .util -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                                docker-compose -f docker-compose.jenkins.yml down
                            """

                            junit 'reports/junit/*.xml'
                        }
                    }
                }
            }

            stage('Sonar Scan') {
                gitlabCommitStatus('Sonar Scan') {
                    withSonarQubeEnv('sonarqube') {
                        withCredentials([string(credentialsId: 'SONAR_DB_PASSWD', variable: 'SONAR_DB_PASSWD')]) {
                        ansiColor('xterm') {
                                sh "/data/sonar-scanner/bin/sonar-scanner -Dsonar.host.url=http://10.72.20.32:9000"
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
                gitlabCommitStatus('Deploy test image') {
                    if (isDev || isRelease) {
                        test_images.each { def image ->
                            ansiColor('xterm') {
                                withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                    image.push()
                                }
                            }
                        }
                    }
                }
            }

            stage('Build pip package') {
                gitlabCommitStatus('Build pip package') {
                    if (isDev || isRelease) {
                        withEnv(["TAG=${testTag}"]) {
                            writeFile('VERSION', env.GIT_TAG)

                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins 'cd docs && make html'
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins 'tar cvzf docs/html-${env.GIT_TAG}.tar.gz -C doc/build html'
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins 'python setup.py bdist_wheel sdist'
                                docker-compose -f docker-compose.jenkins.yml down
                            """
                        }
                    }
                }
            }

            stage ('Publishing documentation') {
                gitlabCommitStatus('Publishing documentation') {
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

            stage('Publishing package to Artifactory') {
                gitlabCommitStatus('Publishing package to Artifactory') {
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
    } finally {
        stage('Cleanup') {
            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('platform/python:2.7').inside("-u root"){
                sh script: ''' \
                    rm -rf .[A-z0-9]*
                    rm -rf *
                ''', returnStdout: true
            }
            deleteDir()
        }
    }
}
