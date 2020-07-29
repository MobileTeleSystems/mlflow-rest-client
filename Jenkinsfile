#!groovy

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

Boolean isMaster = false
Boolean isDev = true
Boolean isRelease = false

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

            String testTag = isMaster ? 'test'   : 'dev-test'

            List pythonVersions = ['2.7', '3.6', '3.7']

            List test_images = []
            def docs_images

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    pythonVersions.each{ def version ->
                        def testTagVersioned = "${testTag}-python${version}"

                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    def cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}")
                                    cache.pull()
                                } catch (Exception e) {
                                }

                                test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}", "--build-arg PYTHON_VERSION=${version} --force-rm -f Dockerfile.test .")
                            }
                        }
                    }
                    ansiColor('xterm') {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            try {
                                def cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}")
                                cache.pull()
                            } catch (Exception e) {
                            }

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
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'python -m pylint .mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
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
                        withEnv(["TAG=${testTag}"]) {
                            def package_version = readFile('VERSION').trim()

                            sh script: """
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'cd docs && make html'
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'tar cvzf docs/html-${package_version}.tar.gz -C docs/build/html .'
                                docker-compose -f docker-compose.jenkins.yml run --rm --no-deps mlflow-client-jenkins bash -c 'python setup.py bdist_wheel sdist'
                                docker-compose -f docker-compose.jenkins.yml down
                            """
                        }
                    }
                }
            }

            stage ('Building documentation') {
                gitlabCommitStatus('Building documentation') {
                    if (isRelease) {
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
                   ansiColor('xterm') {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            def package_version = readFile('VERSION').trim()
                            try {
                                def cache = docker.image("docker.rep.msk.mts.ru/mlflow-client.nginx:${package_version}")
                                cache.pull()
                            } catch (Exception e) {
                            }

                            docs_images = docker.build("docker.rep.msk.mts.ru/mlflow-client.nginx:${package_version}", "--force-rm -f ./nginx/Dockerfile_nginx .")
                            docs_images.push()
                        }
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('platform/python:2.7').inside("-u root") {
                sh script: ''' \
                    rm -rf .[A-z0-9]*
                    rm -rf *
                ''', returnStdout: true
            }
            deleteDir()
        }
    }
}

gitlabCommitStatus(name: 'Deploying the documentation to the nginx server') {
    node('bdcigate01'){
        stage ('Deploying the documentation') {
            deleteDir()
            checkout scm

    	    def package_version = readFile('VERSION').trim()

	        ansiblePlaybook(
	            playbook: './ansible/docs_nginx_deployment.yml',
		        extraVars: [
    		         target_host: "10.73.40.6",
    	             docs_version: package_version
           		],
    		    extras: '-vv'
	        )

            deleteDir()
	    }
    }
}
