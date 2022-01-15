/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * The OpenSearch Contributors require contributions made to
 * this file be licensed under the Apache-2.0 license or a
 * compatible open source license.
 */

void call(Map args = [:]) {
    def lib = library(identifier: 'jenkins@20211123', retriever: legacySCM(scm))

    // fileActions are a closure that accepts a String, filepath with return type void
    List<Closure> fileActions = args.fileActions ?: []

    String manifest = args.manifest ?: "manifests/${INPUT_MANIFEST}"
    def inputManifest = lib.jenkins.InputManifest.new(readYaml(file: manifest))
    String filename = inputManifest.build.getFilename()
    String version = inputManifest.build.version

    def artifactPath = "${DISTRIBUTION_JOB_NAME}/${version}/${DISTRIBUTION_BUILD_NUMBER}/${DISTRIBUTION_PLATFORM}/${DISTRIBUTION_ARCHITECTURE}"

    withAWS(role: "${ARTIFACT_DOWNLOAD_ROLE_NAME}", roleAccount: "${AWS_ACCOUNT_PUBLIC}", duration: 900, roleSessionName: 'jenkins-session') {
        s3Download(bucket: "${ARTIFACT_BUCKET_NAME}", file: "$WORKSPACE/artifacts", path: "${artifactPath}/",  force: true)
    }

    String build_manifest = "artifacts/$artifactPath/builds/$filename/manifest.yml"
    def buildManifest = readYaml(file: build_manifest)

    print("Actions ${fileActions}")

    argsMap = [:]
    argsMap['signatureType'] = '.sig'

    print("filename is ${filename}")


    if(filename == "opensearch") {
        //////////// Signing Artifacts
        println("Signing Core Pluings")
        String corePluginDir = "$WORKSPACE/artifacts/$artifactPath/builds/$filename/core-plugins"
        argsMap['artifactPath'] = corePluginDir
    }


    print("before action")
    for (Closure action : fileActions) {
        print("running action ${action}")
        action(argsMap)
    }

    println("Signing TAR Artifacts")
    String coreFullPath = ['core', filename, version].join('/')
    String bundleFullPath = ['bundle', filename, version].join('/')
    for (Closure action : fileActions) {
        for (file in findFiles(glob: "**/${filename}-min-${version}*.tar.gz,**/${filename}-${version}*.tar.gz")) {
            argsMap['artifactPath'] = "$WORKSPACE" + "/" + file.getPath()
            action(argsMap)
        }
    }




    //////////// Uploading Artifacts
    withAWS(role: "${ARTIFACT_PROMOTION_ROLE_NAME}", roleAccount: "${AWS_ACCOUNT_ARTIFACT}", duration: 900, roleSessionName: 'jenkins-session') {
        println("filename is " + filename)
        if(filename == "opensearch") {
            List<String> corePluginList = buildManifest.components.artifacts."core-plugins"[0]
            for (String pluginSubPath : corePluginList) {
                String pluginSubFolder = pluginSubPath.split('/')[0]
                String pluginNameWithExt = pluginSubPath.split('/')[1]
                String pluginName = pluginNameWithExt.replace('-' + version + '.zip', '')
                String pluginNameNoExt = pluginNameWithExt.replace('-' + version, '')
                String pluginFullPath = ['plugins', pluginName, version].join('/')
                s3Upload(
                    bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}",
                    path: "releases-test/$pluginFullPath/",
                    workingDir: "$WORKSPACE/artifacts/$artifactPath/builds/$filename/core-plugins/",
                    includePathPattern: "**/${pluginName}*"
                )
            }

        }
      
        s3Upload(
            bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}",
            path: "releases-test/$coreFullPath/",
            workingDir: "$WORKSPACE/artifacts/$artifactPath/builds/$filename/dist/",
            includePathPattern: "**/${filename}-min-${version}*")


        s3Upload(
            bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}",
            path: "releases-test/$bundleFullPath/",
            workingDir: "$WORKSPACE/artifacts/$artifactPath/dist/$filename/",
            includePathPattern: "**/${filename}-${version}*")

        // upload build and dist manifest
        s3Upload(
            bucket: "${ARTIFACT_PRODUCTION_BUCKET_NAME}",
            path: "releases-test/$version/",
            workingDir: "$WORKSPACE/artifacts/$artifactPath/",
            includePathPattern: "**/")

    }
}
