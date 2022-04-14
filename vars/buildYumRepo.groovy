void call(Map args = [:]) {
    lib = library(identifier: 'jenkins@20211123', retriever: legacySCM(scm))

    def buildManifest = lib.jenkins.BuildManifest.new(readYaml(file: args.buildManifest))
    echo "Create yum repo metadata and repo file ${args.buildManifest}"

    def filename = buildManifest.build.getFilename()
    def name = buildManifest.build.name
    def version = buildManifest.build.version
    def repoFilePath = "rpm/dist/${filename}"

    sh([
        'createrepo',
        "\"${repoFilePath}\"",
    ].join(' '))

    def repoFileContent = [
        "[${filename}-${version}-${BUILD_NUMBER}-staging]",
        "name=${name} ${version} ${BUILD_NUMBER} Staging",
        "baseurl=${args.baseUrl}/rpm/dist/${filename}/",
        "enabled=1",
        "autorefresh=1",
        "type=rpm-md"
    ].join('\n')

    writeFile file: "${repoFilePath}/${filename}-${version}.staging.repo", text: repoFileContent
}
