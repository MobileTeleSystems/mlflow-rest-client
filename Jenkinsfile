#!groovy

@Library('jenkins_lib') _

def project = 'mlflow-client'

def docker_registry = 'docker.rep.msk.mts.ru'
def docker_image = "bigdata/platform/dsx/${project}"

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

String git_tag
String git_branch
String git_commit

Boolean isMaster = false
Boolean isDev = true
Boolean isTagged = false
Boolean isRelease = false

String testTag
String prodTag
String version
String release
String docker_version

List pythonVersions = ['2.7', '3.6', '3.7']

node('adm-ci') {
    try {
        gitlabBuilds(builds: [
            "Build test images",
            "Run unit tests",
            "Run integration tests",
            "Check coverage",
            "Pylint",
            "Sonar Scan",
            "Retrieve Sonar Results",
            "Build documentation",
            "Publish package & documentation",
            "Cleanup Artifactory",
            "Deploy documentation"
        ]) {
            stage('Checkout') {
                def scmVars = checkout scm
                git_commit = scmVars.GIT_COMMIT

                git_tag = sh(script: "git describe --tags --abbrev=0 --exact-match || exit 0", returnStdout: true).trim()
                if (git_tag == 'null' || git_tag == '') {
                    git_tag = null
                }

                git_branch = scmVars.CHANGE_BRANCH ?: env.BRANCH_NAME ?: scmVars.GIT_BRANCH
                git_branch = git_branch.replace('origin/', '').replace('feature/', '').trim()

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
            isTagged  = !!git_tag
            isRelease = isMaster && isTagged
            version = git_tag ? git_tag.replaceAll(/^v/, '') : null
            docker_version = version ? version.replace('.dev', '-dev') : null
            release = version ? version.replaceAll(/\.dev[\d]+/, '') : null

            testTag = isDev ? 'dev-test' : 'test'
            prodTag = isDev ? 'dev'      : 'latest'

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    def build = [
                        failFast: true
                    ]

                    withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                        pythonVersions.each { def pythonVersion ->
                            ['unit', 'integration'].each { String suffix ->
                                def testTagVersioned = "${testTag}-${suffix}-python${pythonVersion}"

                                build["${pythonVersion}-${suffix}"] = {
                                    ansiColor('xterm') {
                                        docker.build("${docker_registry}/${docker_image}:${testTagVersioned}-${env.BUILD_TAG}", "--build-arg CACHEBUST=\$(date +%s) --build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.${suffix} .")
                                    }
                                }
                            }
                        }
                        parallel build

                        ['unit', 'integration'].each { String suffix ->
                            ansiColor('xterm') {
                                docker.build("${docker_registry}/${docker_image}:${testTag}-${suffix}-${env.BUILD_TAG}", "--build-arg CACHEBUST=\$(date +%s) --force-rm -f Dockerfile.${suffix} .")
                            }
                        }
                    }
                }
            }

            docker.image("${docker_registry}/${docker_image}:${testTag}-unit-${env.BUILD_TAG}").inside("--entrypoint=''") {
                try {
                    version = sh script: "python setup.py --version", returnStdout: true
                    version = version.trim()
                    docker_version = version ? version.replace('.dev', '-dev') : null
                    release = version ? version.replaceAll(/\.dev[\d]+/, '') : null
                } catch (Exception e) {}
            }

            stage('Run unit tests') {
                gitlabCommitStatus('Run unit tests') {
                    def build = [
                        failFast: true
                    ]
                    pythonVersions.each { def pythonVersion ->
                        build[pythonVersion] = {
                            withEnv(["TAG=${testTag}-unit-python${pythonVersion}-${env.BUILD_TAG}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${pythonVersion}" run --rm mlflow-client-jenkins-unit
                                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${pythonVersion}" down
                                    """
                                }
                            }
                        }
                    }
                    parallel build
                }
            }

            stage('Run integration tests') {
                gitlabCommitStatus('Run integration tests') {
                    def build = [
                        failFast: true
                    ]
                    pythonVersions.each { def pythonVersion ->
                        build[pythonVersion] = {
                            withEnv(["TAG=${testTag}-integration-python${pythonVersion}-${env.BUILD_TAG}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${pythonVersion}" run --rm mlflow-client-jenkins-integration
                                        docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${pythonVersion}" down
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
                    withEnv(["TAG=${testTag}-unit-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint coverage.sh mlflow-client-jenkins-unit
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down
                            """
                        }
                    }

                    junit 'reports/junit/*.xml'
                }
            }

            stage('Pylint') {
                gitlabCommitStatus('Pylint') {
                    withEnv(["TAG=${testTag}-unit-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit -c 'python -m pylint .mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down
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
                                if (isDev || isTagged) {
                                    sh "/data/sonar-scanner/bin/sonar-scanner -Dsonar.projectVersion=${version}"
                                } else {
                                    sh "/data/sonar-scanner/bin/sonar-scanner"
                                }
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

            stage('Build pip package') {
                gitlabCommitStatus('Build pip package') {
                    //Build wheels for each version
                    pythonVersions.each { def pythonVersion ->
                        def testTagVersioned = "${testTag}-unit-python${pythonVersion}-${env.BUILD_TAG}"

                        docker.image("${docker_registry}/${docker_image}:${testTagVersioned}").inside("--entrypoint=''") {
                            ansiColor('xterm') {
                                sh script: """
                                    python setup.py bdist_wheel sdist
                                """
                            }
                        }
                    }
                }
            }

            stage ('Build documentation') {
                gitlabCommitStatus('Build documentation') {
                    docker.image("${docker_registry}/${docker_image}:${testTag}-unit-${env.BUILD_TAG}").inside("--entrypoint=''") {
                        ansiColor('xterm') {
                            sh script: """
                                cd docs
                                make html
                                tar cvzf html-${version}.tar.gz -C build/html .
                            """
                        }

                        if (isRelease) {
                            ansiColor('xterm') {
                                sh script: """
                                    cd docs
                                    cp html-${version}.tar.gz html-latest.tar.gz
                                """
                            }
                        }
                    }
                }
            }

            stage ('Publish package & documentation') {
                gitlabCommitStatus('Publish package & documentation') {
                    if (isDev || isTagged) {
                        def uploadSpec = '''{
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

                        def buildInfo = server.upload spec: uploadSpec
                        server.publishBuildInfo buildInfo
                    }
                }
            }

            stage('Cleanup Artifactory') {
                gitlabCommitStatus('Cleanup Artifactory') {
                    if (isDev || isTagged) {
                        build job: 'artifactory-cleanup', propagate: false, parameters: [
                            [$class: 'StringParameterValue',  name: 'PACKAGE_NAME',         value: project],
                            [$class: 'StringParameterValue',  name: 'PACKAGE_TYPE',         value: 'pypi'],
                            [$class: 'BooleanParameterValue', name: 'REMOVE_PYPI',          value: true],
                            [$class: 'BooleanParameterValue', name: 'REMOVE_DOCKER_IMAGES', value: false],
                            [$class: 'BooleanParameterValue', name: 'REMOVE_DOCS',          value: true],
                            [$class: 'BooleanParameterValue', name: 'DRY_RUN',              value: false]
                        ]
                    }
                }
            }

            stage('Deploy documentation') {
                gitlabCommitStatus('Deploy documentation') {
                    if (isDev || isTagged) {
                        build job: 'nginx-build', parameters: [
                            [$class: 'StringParameterValue',  name: 'PROJECT_NAME', value: project],
                            [$class: 'StringParameterValue',  name: 'IMAGE_NAME',   value: docker_image],
                            [$class: 'StringParameterValue',  name: 'VERSION',      value: docker_version],
                            [$class: 'BooleanParameterValue', name: 'DRY_RUN',      value: false]
                        ]
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
            def build = [
                failFast: false
            ]

            ['unit', 'integration'].each { String suffix ->
                pythonVersions.each { def pythonVersion ->
                    build["${suffix}-${pythonVersion}"] = {
                        withEnv(["TAG=${testTag}-${suffix}-python${pythonVersion}-${env.BUILD_TAG}"]) {
                            ansiColor('xterm') {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins-${suffix}.yml -p "${suffix}-${env.BUILD_TAG}-${pythonVersion}" down || true
                                    docker rmi ${docker_registry}/${docker_image}:\$TAG || true
                                """
                            }
                        }
                    }
                }

                build[suffix] = {
                    withEnv(["TAG=${testTag}-${suffix}-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-${suffix}.yml -p "${suffix}-${env.BUILD_TAG}" down || true
                                docker rmi ${docker_registry}/${docker_image}:\$TAG || true
                            """
                        }
                    }
                }
            }

            parallel build

            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('platform/python:3.7').inside("-u root") {
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