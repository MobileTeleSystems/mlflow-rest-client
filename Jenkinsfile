#!groovy

@Library('jenkins_lib') _

String project = 'mlflow-client'

String docker_registry = 'docker.rep.msk.mts.ru'
String docker_image = "bigdata/platform/dsx/${project}"

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

String git_tag
String git_branch
String git_commit

Boolean is_master = false
Boolean is_dev = false
Boolean is_prerelease = false
Boolean is_bug = false
Boolean is_hotfix = false
Boolean is_feature = false

Boolean is_tagged = false
Boolean is_release_branch=false
Boolean is_release = false

String version
String release
String docker_version
String jira_task

List python_versions = ['2.7', '3.6', '3.7', '3.8', '3.9']

node('adm-ci') {
    try {
        gitlabBuilds(builds: [
            "Build test images",
            "Run unit tests",
            "Run integration tests",
            "Check coverage",
            "Pylint",
            "Bandit",
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
                git_branch = git_branch.replace('origin/', '').trim()

                println(git_tag)
                println(git_branch)
                println(git_commit)

                sh script: """
                    mkdir -p ./reports/junit
                    touch ./reports/pylint.txt
                    chmod 777 -R ./reports
                """
            }

            is_master     = git_branch == 'master'
            is_dev        = git_branch in ['dev', 'develop']
            is_bug        = git_branch.contains('bug')
            is_feature    = git_branch.contains('feature')
            is_prerelease = git_branch.contains('release')
            is_hotfix     = git_branch.contains('hotfix')

            is_tagged  = !!git_tag
            is_release_branch = is_master
            is_release = is_release_branch && is_tagged

            jira_task = git_branch.split('/').size() > 1 ? git_branch.split('/')[-1] : null

            version = git_tag ? git_tag.replaceAll(/^v/, '') : null
            docker_version = version ? version.replace('.dev', '-dev') : null
            release = version ? version.replaceAll(/\.dev[\d]+/, '') : null

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    def build = [
                        failFast: true
                    ]

                    withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: "https://${docker_registry}"]) {
                        python_versions.each { def python_version ->
                            ['unit', 'integration'].each { String suffix ->
                                try {
                                    docker.image("python:${python_version}-slim").pull()
                                } catch (Exception e) {}

                                def test_tag_versioned = "${suffix}-python${python_version}"

                                build["${python_version}-${suffix}"] = {
                                    ansiColor('xterm') {
                                        docker.build("${docker_registry}/${docker_image}:${test_tag_versioned}-${env.BUILD_ID}", "--build-arg CACHEBUST=\$(date +%s) --build-arg PYTHON_VERSION=${python_version} --force-rm -f Dockerfile.${suffix} .")
                                    }
                                }
                            }
                        }
                        parallel build

                        ['unit', 'integration'].each { String suffix ->
                            ansiColor('xterm') {
                                docker.build("${docker_registry}/${docker_image}:${suffix}-${env.BUILD_ID}", "--build-arg CACHEBUST=\$(date +%s) --force-rm -f Dockerfile.${suffix} .")
                            }
                        }
                    }
                }
            }

            docker.image("${docker_registry}/${docker_image}:unit-${env.BUILD_ID}").inside("--entrypoint=''") {
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
                    python_versions.each { def python_version ->
                        build[python_version] = {
                            withEnv(["TAG=unit-python${python_version}-${env.BUILD_ID}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${python_version}" run --rm mlflow-client-jenkins-unit
                                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${python_version}" down -v
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
                    python_versions.each { def python_version ->
                        build[python_version] = {
                            withEnv(["TAG=integration-python${python_version}-${env.BUILD_ID}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${python_version}" run --rm mlflow-client-jenkins-integration
                                        docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${python_version}" down -v
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
                    withEnv(["TAG=unit-${env.BUILD_ID}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit coverage.sh
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v
                                sed -i 's#/app#${env.WORKSPACE}#g' reports/coverage*.xml
                            """
                        }
                    }

                    junit 'reports/junit/*.xml'
                }
            }

            stage('Pylint') {
                gitlabCommitStatus('Pylint') {
                    withEnv(["TAG=unit-${env.BUILD_ID}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit -c 'python -m pylint mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v
                            """
                        }
                    }
                }
            }

            stage('Bandit') {
                gitlabCommitStatus('Bandit') {
                    withEnv(["TAG=unit-${env.BUILD_ID}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit -c 'python -m bandit -r mlflow_client -f json -o ./reports/bandit.json || true'
                                docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v
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
                                if (is_dev || is_tagged) {
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
                    python_versions.each { def python_version ->
                        def test_tag_versioned = "unit-python${python_version}"

                        docker.image("${docker_registry}/${docker_image}:${test_tag_versioned}-${env.BUILD_ID}").inside("--entrypoint=''") {
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
                    docker.image("${docker_registry}/${docker_image}:unit-${env.BUILD_ID}").inside("--entrypoint='' -u root") {
                        ansiColor('xterm') {
                            sh script: """
                                cd docs
                                make html
                                tar cvzf html-${version}.tar.gz -C build/html .
                            """
                        }

                        if (is_release) {
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
                    if (is_dev || is_tagged) {
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
                    if (is_dev || is_tagged) {
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
                    if (is_dev || is_tagged) {
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
                python_versions.each { def python_version ->
                    build["${suffix}-${python_version}"] = {
                        withEnv(["TAG=${suffix}-python${python_version}-${env.BUILD_ID}"]) {
                            ansiColor('xterm') {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins-${suffix}.yml -p "${suffix}-${env.BUILD_TAG}-${python_version}" down -v || true
                                    docker rmi ${docker_registry}/${docker_image}:\$TAG || true
                                """
                            }
                        }
                    }
                }

                build[suffix] = {
                    withEnv(["TAG=${suffix}-${env.BUILD_ID}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins-${suffix}.yml -p "${suffix}-${env.BUILD_TAG}" down -v || true
                                docker rmi ${docker_registry}/${docker_image}:\$TAG || true
                            """
                        }
                    }
                }
            }

            parallel build

            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('alpine').inside("-u root") {
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
