def call(Map args = [:]) {
    def lib = library(identifier: 'jenkins@20211123', retriever: legacySCM(scm))
    def inputManifestObj = lib.jenkins.InputManifest.new(readYaml(file: args.inputManifest))

    buildManifest(args)

    String buildManifest = "${args.distribution}/builds/${inputManifestObj.build.getFilename()}/manifest.yml"
    def buildManifestObj = lib.jenkins.BuildManifest.new(readYaml(file: buildManifest))

    if (args.distribution == 'rpm') {
        // need to create yum repo
        sh([
            'createrepo',
            "\"${args.distribution}/dist/${inputManifestObj.build.getFilename()}\"",
        ].join(' '))
    }

    assembleUpload(
        args + [
            buildManifest: buildManifest,
        ]
    )

    return buildManifestObj
}
