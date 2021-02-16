#!groovy

@Library('jenkins_lib') _

String project = 'mlflow-client'

String docker_registry = 'docker.rep.msk.mts.ru'
String docker_image = "bigdata/platform/dsx/${project}"

String git_tag
List git_branches
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

pipeline {
    agent {
        label 'adm-ci'
    }

    options {
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    def scmVars = checkout scm
                    git_commit = scmVars.GIT_COMMIT

                    git_tag = sh(script: "git describe --tags --abbrev=0 --exact-match || exit 0", returnStdout: true).trim()
                    if (git_tag == 'null' || git_tag == '') {
                        git_tag = null
                    }

                    List branches = sh(script: """
                        git branch -a --no-abbrev --contains $git_commit | egrep -v "(detached|->)" | cut -c 3-
                    """, returnStdout: true).trim().split('\n')

                    git_branches = [scmVars.CHANGE_BRANCH, env.BRANCH_NAME, scmVars.GIT_BRANCH] + branches
                    git_branches = git_branches.findAll{ it }.collect{ it.replace('remotes/', '').replace('origin/', '').trim() }
                    git_branches.unique()

                    println(git_tag)
                    println(git_branches)
                    println(git_commit)

                    sh script: """
                        mkdir -p ./reports/junit
                        touch ./reports/pylint.txt
                        chmod 777 -R ./reports
                    """

                    is_master     = 'master' in git_branches || 'main' in git_branches
                    is_dev        = 'dev' in git_branches || 'develop' in git_branches
                    is_bug        = git_branches.collect{ it.contains('bug') }
                    is_feature    = git_branches.collect{ it.contains('feature') }
                    is_prerelease = git_branches.collect{ it.contains('release') }
                    is_hotfix     = git_branches.collect{ it.contains('hotfix') }

                    is_tagged  = !!git_tag
                    is_release_branch = is_master
                    is_release = is_release_branch && is_tagged

                    jira_task = git_branches.collect{ it.split('/').size() > 1 ? it.split('/')[-1] : null }.find { it }

                    version = git_tag ? git_tag.replaceAll(/^v/, '') : null
                    docker_version = version ? version.replace('.dev', '-dev') : null
                    release = version ? version.replaceAll(/\.dev[\d]+/, '') : null
                }
            }
        }

        stage('Build test images') {
            steps {
                gitlabCommitStatus('Build test images') {
                    script {
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
                                        docker.build("${docker_registry}/${docker_image}:${test_tag_versioned}-${env.BUILD_ID}", "--build-arg BUILD_ID=\$BUILD_ID --build-arg PYTHON_VERSION=${python_version} --force-rm -f Dockerfile.${suffix} .")
                                    }
                                }
                            }
                            parallel build

                            ['unit', 'integration'].each { String suffix ->
                                docker.build("${docker_registry}/${docker_image}:${suffix}-${env.BUILD_ID}", "--build-arg BUILD_ID=\$BUILD_ID --force-rm -f Dockerfile.${suffix} .")
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
                    }
                }
            }
        }

        stage('Run unit tests') {
            steps {
                gitlabCommitStatus('Run unit tests') {
                    script {
                        def build = [
                            failFast: true
                        ]
                        python_versions.each { def python_version ->
                            build[python_version] = {
                                withEnv(["TAG=unit-python${python_version}-${env.BUILD_ID}"]) {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${python_version}" run --rm mlflow-client-jenkins-unit
                                    """
                                }
                            }
                        }
                        parallel build
                    }
                }
            }

            post {
                cleanup {
                    script {
                        python_versions.each { def python_version ->
                            withEnv(["TAG=unit-python${python_version}-${env.BUILD_ID}"]) {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}-${python_version}" down -v || true
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Run integration tests') {
            steps {
                gitlabCommitStatus('Run integration tests') {
                    script {
                        def build = [
                            failFast: true
                        ]
                        python_versions.each { def python_version ->
                            build[python_version] = {
                                withEnv(["TAG=integration-python${python_version}-${env.BUILD_ID}"]) {
                                    sh script: """
                                        docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${python_version}" run --rm mlflow-client-jenkins-integration
                                    """
                                }
                            }
                        }
                        parallel build
                    }
                }
            }

            post {
                cleanup {
                    script {
                        python_versions.each { def python_version ->
                            withEnv(["TAG=integration-python${python_version}-${env.BUILD_ID}"]) {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins-integration.yml -p "integration-${env.BUILD_TAG}-${python_version}" down -v || true
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Check coverage') {
            environment {
                TAG = "unit-${env.BUILD_ID}"
            }

            steps {
                gitlabCommitStatus('Check coverage') {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit coverage.sh
                        sed -i 's#/app#${env.WORKSPACE}#g' reports/coverage*.xml
                    """

                    junit 'reports/junit/*.xml'
                }
            }

            post {
                cleanup {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v || true
                    """
                }
            }
        }

        stage('Pylint') {
            environment {
                TAG = "unit-${env.BUILD_ID}"
            }

            steps {
                gitlabCommitStatus('Pylint') {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit -c 'python -m pylint mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero' > ./reports/pylint.txt
                    """
                }
            }

            post {
                cleanup {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v || true
                    """
                }
            }
        }

        stage('Bandit') {
            environment {
                TAG = "unit-${env.BUILD_ID}"
            }

            steps {
                gitlabCommitStatus('Bandit') {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" run --rm --no-deps --entrypoint bash mlflow-client-jenkins-unit -c 'python -m bandit -r mlflow_client -f json -o ./reports/bandit.json || true'
                    """
                }
            }

            post {
                cleanup {
                    sh script: """
                        docker-compose -f docker-compose.jenkins-unit.yml -p "unit-${env.BUILD_TAG}" down -v || true
                    """
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
            steps {
                gitlabCommitStatus('Retrieve Sonar Results') {
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
                        //Build wheels for each version
                        python_versions.each { def python_version ->
                            def test_tag_versioned = "unit-python${python_version}"

                            docker.image("${docker_registry}/${docker_image}:${test_tag_versioned}-${env.BUILD_ID}").inside("--entrypoint=''") {
                                sh script: """
                                    python setup.py bdist_wheel sdist
                                """
                            }
                        }
                    }
                }
            }
        }

        stage ('Build documentation') {
            steps {
                gitlabCommitStatus('Build documentation') {
                    script {
                        docker.image("${docker_registry}/${docker_image}:unit-${env.BUILD_ID}").inside("--entrypoint='' -u root") {
                            sh script: """
                                cd docs
                                make html
                                tar cvzf html-${version}.tar.gz -C build/html .
                            """

                            if (is_release) {
                                sh script: """
                                    cd docs
                                    cp html-${version}.tar.gz html-latest.tar.gz
                                """
                            }
                        }
                    }
                }
            }
        }

        stage ('Publish package & documentation') {
            when {
                expression { is_dev || is_tagged }
            }

            steps {
                gitlabCommitStatus('Publish package & documentation') {
                    rtUpload (
                        serverId: 'rep.msk.mts.ru',
                        spec: '''
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
            when {
                expression { is_dev || is_tagged }
            }

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
            when {
                expression { is_dev || is_tagged }
            }

            steps {
                gitlabCommitStatus('Deploy documentation') {
                    build job: 'nginx-build', parameters: [
                        string(name: 'PROJECT_NAME',  value: project),
                        string(name: 'IMAGE_NAME',    value: docker_image),
                        string(name: 'VERSION',       value: docker_version),
                        booleanParam(name: 'DRY_RUN', value: false)
                    ]
                }
            }
        }
    }

    post {
        cleanup {
            script {
                def build = [
                    failFast: false
                ]

                ['unit', 'integration'].each { String suffix ->
                    python_versions.each { def python_version ->
                        build["${suffix}-${python_version}"] = {
                            sh script: """
                                docker rmi ${docker_registry}/${docker_image}:${suffix}-python${python_version}-${env.BUILD_ID} || true
                            """
                        }
                    }

                    build[suffix] = {
                        sh script: """
                            docker rmi ${docker_registry}/${docker_image}:${suffix}-${env.BUILD_ID} || true
                        """
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
}
