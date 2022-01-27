const aws = require('aws-sdk');

const s3 = new aws.S3({ apiVersion: '2006-03-01' });

exports.handler = async (event, context) => {

    const request = event.Records[0].cf.request;
    request.uri = request.uri.replace(/^\/ci\/...\//, '\/')
    callback(null, request);

    // Below is the working in progress logic to get the max build number under a version.
    // Hardcode the version to be 1.2.0 and bucket name to test-access-1-20 for demo purpose.
    console.log('Received event:', JSON.stringify(event, null, 2));

    // Get the object from the event and show its content type
    const bucket = "test-access-1-20";

    // Create the parameters for calling listObjects
    var bucketParams = {
        Bucket: bucket,
        Prefix: '1.2.0/',
        Delimiter: '/'
    };

    try {
        const s3Response = await s3.listObjects(bucketParams).promise();

        const commonPrefixes = s3Response.CommonPrefixes;

        var maxBuildNumber = 0;

        commonPrefixes.forEach((prefix) => {
            // e.g '1.2.0/21/'
            const value = prefix['Prefix'];

            const reg = /\/(\d+)/;

            const result = value.match(reg);



            if (result) {
                const number = parseInt(result[1]);
                if (number > maxBuildNumber) {
                    maxBuildNumber = number;
                }
            }
        }
        );

        console.log('maxBuildNumber', maxBuildNumber);
    }
    catch (ex) {
        // if failed
        // handle response here (obv: ex object)
        // you can simply use logging
        console.error(ex);
    }
};
