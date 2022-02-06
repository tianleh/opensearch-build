void call(Map args = [:]) {
    def lib = library(identifier: 'jenkins@20211123', retriever: legacySCM(scm))

    def buildManifest = lib.jenkins.BuildManifest.new(readYaml(file: args.buildManifest))
    def minArtifactPath = buildManifest.getMinArtifact()
    def productFilename = buildManifest.build.getFilename()
    def packageName = buildManifest.build.getPackageName()

    def artifactPath = buildManifest.getArtifactRoot("${JOB_NAME}", "${BUILD_NUMBER}")
    echo "Uploading to s3://${ARTIFACT_BUCKET_NAME}/${artifactPath}"

    uploadToS3(
            sourcePath: 'builds',
            bucket: "${ARTIFACT_BUCKET_NAME}",
            path: "${artifactPath}/builds"
    )

    uploadToS3(
            sourcePath: 'dist',
            bucket: "${ARTIFACT_BUCKET_NAME}",
            path: "${artifactPath}/dist"
    )

    def indexYamlPath = buildManifest.getIndexYamlRoot("${JOB_NAME}")
    def latestBuildData = ['latest': "${BUILD_NUMBER}"]
    writeYaml file: 'index.yml', data: latestBuildData

    def read = readYaml file: 'index.yml'

    echo "file content is ${read}"

    def ret = sh(script: 'ls -l', returnStdout: true)

    println ret

    echo "Uploading index.yml to s3://${ARTIFACT_PRODUCTION_BUCKET_NAME}/${indexYamlPath}"

    uploadToS3(
            sourcePath: 'index.yml',
            bucket: "${ARTIFACT_BUCKET_NAME}",
            path: "${indexYamlPath}/dist/index.yml"
    )
        

    echo "Uploading to s3://${ARTIFACT_PRODUCTION_BUCKET_NAME}/${artifactPath}"

    withAWS(role: "${ARTIFACT_PROMOTION_ROLE_NAME}", roleAccount: "${AWS_ACCOUNT_ARTIFACT}", duration: 900, roleSessionName: 'jenkins-session') {
        s3Upload(file: "builds/${productFilename}/${minArtifactPath}", bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}", path: "release-candidates/core/${productFilename}/${buildManifest.build.version}/")
        s3Upload(file: "dist/${productFilename}/${packageName}", bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}", path: "release-candidates/bundle/${productFilename}/${buildManifest.build.version}/")
    }

    def baseUrl = buildManifest.getArtifactRootUrl("${PUBLIC_ARTIFACT_URL}", "${JOB_NAME}", "${BUILD_NUMBER}")
    lib.jenkins.Messages.new(this).add("${STAGE_NAME}", [
            "${baseUrl}/builds/${productFilename}/manifest.yml",
            "${baseUrl}/dist/${productFilename}/manifest.yml"
        ].join('\n')
    )
}
