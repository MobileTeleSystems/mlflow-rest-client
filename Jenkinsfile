#!groovy

@Library('jenkins_lib') _

def docker_registry = 'docker.rep.msk.mts.ru'
def docker_image = 'bigdata/platform/dsx/mlflow-client'

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

String git_tag
String git_branch
String git_commit

Boolean isMaster = false
Boolean isDev = true
Boolean isRelease = false

String testTag
String prodTag
String version

List pythonVersions = ['2.7', '3.6', '3.7']

String docs_target_host = 'test_mlflow'

node('bdbuilder04') {
    try {
        gitlabBuilds(builds: ["Build test images", "Run integration tests", "Check coverage", "Pylint", "Sonar Scan", "Retrieve Sonar Results", "Deploy test images", "Build pip package", "Building documentation", "Publishing package to Artifactory", "Build and push nginx docs images", "Check ansible pipeline", "Deploy documentation"]) {
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
            version   = git_tag ? git_tag.replace('v', '') : null

            testTag = isMaster ? 'test' : 'dev-test'
            prodTag = isMaster ? 'latest' : 'dev'

            withCredentials([string(credentialsId: 'vault_token_hdp_pipe', variable: 'vault_token')]) {
                ansibleKey = vault("${env.vault_token}", "platform/ansible/ansible_ssh_key")
                writeFile file: "${env.WORKSPACE}/ansible/ssh.key", text: "${ansibleKey['ansible_ssh_key']}"
            }

            withCredentials([usernameColonPassword(credentialsId: 'sa0000dsscorertest', variable: 'HTTP_PROXY_CREDS')]) {
                withEnv([
                    "HTTP_PROXY=http://${env.HTTP_PROXY_CREDS}@bproxy.msk.mts.ru:3128",
                    "HTTPS_PROXY=http://${env.HTTP_PROXY_CREDS}@bproxy.msk.mts.ru:3128",
                    "NO_PROXY=${env.no_proxy},mlflow-jenkins,localhost,127.0.0.1,*.msk.mts.ru,*.msk.bd-cloud.mts.ru"
                ]) {
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
                                                cache = docker.image("${docker_registry}/${docker_image}:${testTagVersioned}").pull()
                                            } catch (Exception e) {}

                                            docker.build("${docker_registry}/${docker_image}:${testTagVersioned}-${env.BUILD_TAG}", "--build-arg HTTP_PROXY='${env.HTTP_PROXY}' --build-arg HTTPS_PROXY='${env.HTTPS_PROXY}' --build-arg NO_PROXY='${env.NO_PROXY}' --build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .")
                                        }
                                    }
                                }
                                parallel build

                                ansiColor('xterm') {
                                    try {
                                        // Fetch cache
                                        docker.image("${docker_registry}/${docker_image}:${testTag}").pull()
                                    } catch (Exception e) {}

                                    docker.build("${docker_registry}/${docker_image}:${testTag}-${env.BUILD_TAG}", "--build-arg HTTP_PROXY='${env.HTTP_PROXY}' --build-arg HTTPS_PROXY='${env.HTTPS_PROXY}' --build-arg NO_PROXY='${env.NO_PROXY}' --force-rm -f Dockerfile.test .")
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

                                            docker.build("${docker_registry}/${docker_image}:${testTagVersioned}", "--build-arg HTTP_PROXY='${env.HTTP_PROXY}' --build-arg HTTPS_PROXY='${env.HTTPS_PROXY}' --build-arg NO_PROXY='${env.NO_PROXY}' --build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .").push()
                                        }

                                        docker.build("${docker_registry}/${docker_image}:${testTag}", "--build-arg HTTP_PROXY='${env.HTTP_PROXY}' --build-arg HTTPS_PROXY='${env.HTTPS_PROXY}' --build-arg NO_PROXY='${env.NO_PROXY}' --force-rm -f Dockerfile.test .").push()
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

                                    docker.image("${docker_registry}/${docker_image}:${testTagVersioned}").inside() {
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
                            docker.image("${docker_registry}/${docker_image}:${testTag}-${env.BUILD_TAG}").inside() {
                                try {
                                    version = sh script: "python setup.py --version", returnStdout: true
                                    version = version.trim().replace('v', '').replace('.de', '-dev')
                                } catch (Exception e) {}
                            }

                            if (isDev || isRelease) {
                                docker.image("${docker_registry}/${docker_image}:${testTag}-${env.BUILD_TAG}").inside() {
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
                            if (isDev || isRelease) {
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
                            if (isDev || isRelease) {
                                ansiColor('xterm') {
                                    withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                        try {
                                            // Fetch cache
                                            docker.image("${docker_registry}/${docker_image}.nginx:latest").pull()
                                        } catch (Exception e) {}

                                        def docs_image = docker.build("${docker_registry}/${docker_image}.nginx:${version}", "--build-arg VERSION=${version} --force-rm -f ./docs/nginx/Dockerfile_nginx .")
                                        docs_image.push()
                                        docs_image.push(prodTag)
                                    }
                                }
                            }
                        }
                    }

                    docker.image("docker.rep.msk.mts.ru/base/ansible:2.9").inside("-u root --net=host --entrypoint='' -v ${env.WORKSPACE}/:/app/ -v /data/jenkins/.ansible.cfg:/root/.ansible.cfg -v /data/jenkins/.vault_password:/root/.vault_password") {
                        stage ('Check ansible pipeline') {
                            gitlabCommitStatus(name: 'Check ansible pipeline') {
                                sh "cp /app/ansible/ssh.key /root/.ssh/ansible.key && chmod 600 /root/.ssh/ansible.key"
                                ansiColor('xterm') {
                                    sh "ansible-playbook /app/docs/ansible/nginx_deployment.yml -i /app/docs/ansible/inventory.ini -e target_host=${docs_target_host} -e image_version=${version} --syntax-check --list-tasks -vv"
                                }
                            }
                        }

                        stage ('Deploy documentation') {
                            gitlabCommitStatus(name: 'Deploy documentation') {
                                if (isDev || isRelease) {
                                    ansiColor('xterm') {
                                        ansiblePlaybook(
                                            colorized: true,
                                            installation: 'ansible',
                                            playbook: '/app/docs/ansible/nginx_deployment.yml',
                                            inventory: '/app/docs/ansible/inventory.ini',
                                            extraVars: [
                                                target_host: docs_target_host,
                                                image_version: version
                                            ],
                                            extras: '-vv'
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
            def build = [
                failFast: false
            ]

            pythonVersions.each{ def pythonVersion ->
                build[pythonVersion] = {
                    withEnv(["TAG=${testTag}-python${pythonVersion}-${env.BUILD_TAG}"]) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}-${pythonVersion}" down || true
                                docker rmi ${docker_registry}/${docker_image}:\$TAG --no-prune || true
                            """
                        }
                    }
                }
            }


            build['main'] = {
                withEnv(["TAG=${testTag}-${env.BUILD_TAG}"]) {
                    ansiColor('xterm') {
                        sh script: """
                            docker-compose -f docker-compose.jenkins.yml -p "${env.BUILD_TAG}" down || true
                            docker rmi ${docker_registry}/${docker_image}:\$TAG --no-prune || true
                        """
                    }
                }
            }

            parallel build

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