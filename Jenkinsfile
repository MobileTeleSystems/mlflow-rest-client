#!groovy

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

Boolean isMaster = false
Boolean isDev = true
Boolean isRelease = false

String version

node('bdbuilder04') {
    try {
        gitlabBuilds(builds: ["Build test images", "Run unit tests", "Check coverage", "Pylint", "Sonar Scan", "Retrieve Sonar Results", "Deploy test images", "Build pip package", "Building documentation", "Publishing package to Artifactory", "Build and push nginx docs images"]) {
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

            isMaster  = env.GIT_BRANCH == 'master'
            isDev     = env.GIT_BRANCH == 'dev'
            isRelease = isMaster && env.GIT_TAG

            docker.image('platform/python:3.7').inside("-u root") {
                try {
                    version = sh script: 'python setup.py --version', returnStdout: true
                } catch (Exception e) {
                    version = env.GIT
                }
            }

            String testTag = isMaster ? 'test' : 'dev-test'

            List pythonVersions = ['2.7', '3.6', '3.7']

            List test_images = []

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    pythonVersions.each{ def pythonVersion ->
                        def testTagVersioned = "${testTag}-python${pythonVersion}"

                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    // Fetch cache
                                    cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}").pull()
                                } catch (Exception e) {}

                                test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}", "--build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .")
                            }
                        }
                    }
                    ansiColor('xterm') {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            try {
                                // Fetch cache
                                docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").pull()
                            } catch (Exception e) {}

                            test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTag}", "--force-rm -f Dockerfile.test .")
                        }
                    }
                }
            }

            stage('Run unit tests') {
                gitlabCommitStatus('Run unit tests') {
                    pythonVersions.each{ def pythonVersion ->
                        withEnv(["TAG=${testTag}-python${pythonVersion}"]) {
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
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'python -m pylint .mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                                docker-compose -f docker-compose.jenkins.yml down
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
                                //TODO: remove hardcoded URL after DEVOPSMISC-2353
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
                        //Build wheels for each version
                        pythonVersions.each{ def pythonVersion ->
                            withEnv(["TAG=${testTag}-python${pythonVersion}"]) {
                                ansiColor('xterm') {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'python setup.py bdist_wheel sdist'
                                        docker-compose -f docker-compose.jenkins.yml down
                                    """
                                }
                            }
                        }
                    }
                }
            }

            stage ('Building documentation') {
                gitlabCommitStatus('Building documentation') {
                    if (isMaster) {
                        ansiColor('xterm') {
                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'sphinx-multiversion docs docs/build && mv docs/build/master docs/build/latest && tar cvzf docs/html-latest.tar.gz -C docs/build/latest .'
                                docker-compose -f docker-compose.jenkins.yml down
                            """
                        }

                        if (isRelease) {
                            docker.image('platform/python:3.7').inside("-u root") {
                                ansiColor('xterm') {
                                    sh script: """
                                        cp docs/html-latest.tar.gz docs/html-${version}.tar.gz
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
                gitlabCommitStatus('Build nginx and push docs images') {
                    if (isMaster) {
                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    // Fetch cache
                                    docker.image("docker.rep.msk.mts.ru/mlflow-client.nginx:latest").pull()
                                } catch (Exception e) {}

                                def docs_image = docker.build("docker.rep.msk.mts.ru/mlflow-client.nginx:latest", "--force-rm -f ./docs/nginx/Dockerfile_nginx .")
                                docs_image.push()

                                if (isRelease){
                                    docs_image.push(version)
                                }
                            }
                        }
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
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

gitlabCommitStatus(name: 'Deploying the documentation to the nginx server') {
    node('bdbuilder04'){
        stage ('Deploying the documentation') {
            deleteDir()
            checkout scm

            vault_token_cred = 'vault_token_hdp_pipe'
            withCredentials([string(credentialsId: vault_token_cred, variable: 'token')]) {
                ansibleKey = vault("${token}", "platform/ansible/ansible_ssh_key")
                writeFile file: "./ansible.key", text: "${ansibleKey['ansible_ssh_key']}"

                ansiblePlaybook(
                    playbook: './ansible/docs_nginx_deployment.yml',
                    inventory: './ansible/inventory.ini',
                    credentialsId: 'ansible.key',
                    extraVars: [
                        target_host: "test_mlflow",
                        docs_version: 'latest'
                    ],
                    extras: '-vv'
                )
            }

            deleteDir()
        }
    }
}
